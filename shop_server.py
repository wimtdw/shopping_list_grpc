import grpc
from concurrent import futures
import uuid
import shop_pb2
import shop_pb2_grpc


class ShopService(shop_pb2_grpc.ShopServiceServicer):
    def __init__(self):
        self.products = {}

    def CreateProduct(self, request, context):
        product_id = str(uuid.uuid4())
        product = shop_pb2.Product(
            id=product_id, name=request.name, quantity=request.quantity,
            purchased=False)
        print(f'Добавлен продукт {product.name}')
        self.products[product_id] = product
        return product

    def UpdateProduct(self, request, context):
        product = self.products.get(request.id)
        if product:
            product.name = request.name
            product.quantity = request.quantity
            product.purchased = request.purchased
            print(f'Обновлен продукт {product.name}')
            return product
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details('Product not found')
        return shop_pb2.Empty()

    def DeleteProduct(self, request, context):
        if request.id in self.products:
            product = self.products.get(request.id)
            del self.products[request.id]
            print(f'Удален продукт {product.name}')
            return shop_pb2.Empty()
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details('Product not found')
        return shop_pb2.Empty()

    def ListProducts(self, request, context):
        response = shop_pb2.ListProductsResponse()
        response.products.extend(self.products.values())
        print(f'Список продуктов: {self.products}')
        return response


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    shop_pb2_grpc.add_ShopServiceServicer_to_server(ShopService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server is running on port 50051...")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
