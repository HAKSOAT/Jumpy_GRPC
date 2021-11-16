from concurrent import futures
import re

import grpc
from protos_wrapper import jumpy_pb2
from protos_wrapper import jumpy_pb2_grpc
from crawler import JumiaProduct


def get_product_price(product):
    price = re.match(r'[0-9,]+', product['price'])
    if price:
        price = float(price.group().replace(',', ''))
    else:
        price = float('inf')
    return price


class JumiaServicer(jumpy_pb2_grpc.JumiaServicer):
    def __init__(self):
        pass

    def GetProduct(self, request, context):
        index = 0 if not request.index else request.index
        page = 1 if not request.category.page.id else request.category.page.id
        jumia_product = JumiaProduct(request.category.link, page)
        product = jumia_product.get_data(index)
        response = jumpy_pb2.ProductResponse(**product)
        return response

    def GetProducts(self, request, context):
        page = 1 if not request.category.page.id else request.category.page.id
        jumia_product = JumiaProduct(request.category.link, page)
        products = jumia_product.get_data()
        for product in products:
            yield jumpy_pb2.ProductResponse(**product)

    def _get_cheapest_products(self, requests):
        min_products = []
        for request in requests:
            page = 1 if not request.category.page.id else request.category.page.id
            jumia_product = JumiaProduct(request.category.link, page)
            products = jumia_product.get_data()
            min_products.append(min(products, key=lambda x: get_product_price(x)))
        return min_products

    def GetCheapestProduct_Stream(self, request_iterator, context):
        cheapest_product = min(
            self._get_cheapest_products(request_iterator),
            key=lambda x: get_product_price(x)
        )
        return jumpy_pb2.ProductResponse(**cheapest_product)

    def GetCheapestProduct_Message(self, request_iterator, context):
        cheapest_products = self._get_cheapest_products(request_iterator)
        for product in cheapest_products:
            yield jumpy_pb2.ProductResponse(**product)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    jumpy_pb2_grpc.add_JumiaServicer_to_server(
        JumiaServicer(), server
    )
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
