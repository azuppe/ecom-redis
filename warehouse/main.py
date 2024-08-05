from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel


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

class Product(HashModel):
    name:str
    price:float
    quantity:int
    class Meta():
        database = redis
        
@app.post('/product')
def create(product:Product):
    return product.save()

@app.get('/product/{id}')
def get_product(id:str):
    return Product.get(id)

@app.get('/product')
def get_products():
    return [format_produce(id) for id in Product.all_pks()]

@app.delete('/product/{id}')
def delete_product(id:str):
    return Product.delete(id)

def format_produce(id:str):
    return Product.get(id)
