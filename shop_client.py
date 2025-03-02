from flask import Flask, request, render_template
import grpc
import shop_pb2
import shop_pb2_grpc

app = Flask(__name__)

channel = grpc.insecure_channel('localhost:50051')
stub = shop_pb2_grpc.ShopServiceStub(channel)


@app.route('/', methods=['GET', 'POST'])
def index():
    products = []
    if request.method == 'POST':
        if 'action' in request.form:
            action = request.form['action']
            if action == 'create':
                name = request.form['name']
                quantity = int(request.form['quantity'])
                try:
                    response = stub.CreateProduct(
                        shop_pb2.CreateProductRequest(name=name,
                                                      quantity=quantity))
                except grpc.RpcError as e:
                    return f"Error creating product: {e}"
            elif action == 'update':
                product_id = request.form['product_id']
                name = request.form['name']
                quantity = int(request.form['quantity'])
                purchased = request.form.get('purchased') == 'on'
                try:
                    response = stub.UpdateProduct(
                        shop_pb2.UpdateProductRequest(
                                id=product_id, name=name, quantity=quantity,
                                purchased=purchased))
                except grpc.RpcError as e:
                    return f"Error updating product: {e}"
            elif action == 'delete':

                product_id = request.form['product_id']
                try:
                    stub.DeleteProduct(
                        shop_pb2.DeleteProductRequest(id=product_id))
                except grpc.RpcError as e:
                    return f"Error deleting product: {e}"

        try:
            response = stub.ListProducts(shop_pb2.ListProductsRequest())
            products = [{'id': p.id, 'name': p.name, 'quantity': p.quantity,
                         'purchased': p.purchased} for p in response.products]
        except grpc.RpcError as e:
            return f"Error listing products: {e}"

    return render_template('index.html', products=products)


if __name__ == '__main__':
    app.run(debug=True)
