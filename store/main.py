from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel
import requests
from fastapi.background import BackgroundTasks
import time


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=['*'],
    allow_headers=['*']
)

redis =get_redis_connection(
    host='your host',
    port=17029,
    password='you password',
    decode_responses=True,
)

class ProductOrder(HashModel):
    product_id:str
    quantity:int
    class Meta():
        database = redis
        
class Order(HashModel):
    product_id:str
    price:float
    fee: float
    total:float
    quantity: int
    status:str
    class Meta():
        database = redis
    
@app.post('/order')
def create_order(productOrder: ProductOrder, background_tasks:BackgroundTasks):
    req = requests.get(f'http://127.0.0.1:8000/product/{productOrder.product_id}')
    print(req)
    product = req.json()
    print(product)
    fee = product['price'] * productOrder.quantity * 0.02
    
    
    order = Order(
        product_id = productOrder.product_id,
        price = product['price'],
        fee =fee,
        total = product['price'] + fee,
        quantity = productOrder.quantity,
        status = 'pending'
    )
    order.save()
    background_tasks.add_task(order_complete, order)
    return order

@app.get('/orders/{id}')
def get_order(id:str):
    return Order.get(id)
        
@app.get('/orders')
def fetch_orders():
    return [format_orders(id) for id in Order.all_pks()]


def format_orders(id:str):
    return Order.get(id)

def order_complete(order:Order):
    time.sleep(10)
    order.status = 'completed'
    order.save()
    redis.xadd(name='order-completed', fields=order.dict())
    
    
  