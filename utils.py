import csv 
from fastapi import HTTPException
def read_csv():
    with open ("data/items.csv", mode="r",encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)
    
def write_csv(data):
    with open ("data/items.csv","a",newline="",encoding="utf-8") as f:
        writer=csv.writer(f)
        writer.writerow(data)
        
def delete_csv(product_id):
    products = read_csv()
    products = [p for p in products if int(p["id"]) != product_id]

    with open("data/items.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["id", "name", "price"])
        for p in products:
            writer.writerow([p["id"], p["name"],p["price"]])
            
            
def update_csv(product_id: int, name: str, price: float):
    products = read_csv()
    updated = False

    for product in products:
        if int(product["id"]) == product_id:
            product["name"] = name
            product["price"] = price
            updated = True

    if not updated:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    with open("data/items.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["id", "name", "price"])
        for p in products:
            writer.writerow([p["id"], p["name"], p["price"]])

    return {"message": "Producto actualizado"}
            