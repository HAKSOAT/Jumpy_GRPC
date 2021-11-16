import grpc

from protos_wrapper import jumpy_pb2
from protos_wrapper import jumpy_pb2_grpc


def get_product(stub):
    product_request = jumpy_pb2.ProductRequest(
        category=jumpy_pb2.Category(
            link="https://www.jumia.com.ng/smart-watch-bands/xiaomi/"
        ),
        index=4
    )
    response = stub.GetProduct(product_request)
    print(response)
    return response


def get_products(stub):
    product_request = jumpy_pb2.ProductRequest(
        category=jumpy_pb2.Category(
            link="https://www.jumia.com.ng/smart-watch-bands/xiaomi/"
        ),
    )
    response = stub.GetProducts(product_request)
    for product in response:
        print(product)
    return response


def generate_stream_requests():
    links = ["https://www.jumia.com.ng/smart-watch-bands/oraimo/",
             "https://www.jumia.com.ng/smart-watch-bands/xiaomi/",
             "https://www.jumia.com.ng/smart-watch-bands/tecno/"]
    for link in links:
        product_request = jumpy_pb2.ProductRequest(
            category=jumpy_pb2.Category(
                link=link
            ),
        )
        yield product_request


def get_cheapest_product_per_stream(stub):
    response = stub.GetCheapestProduct_Stream(generate_stream_requests())
    print(response)
    return response


def get_cheapest_product_per_message(stub):
    response = stub.GetCheapestProduct_Message(generate_stream_requests())
    for i, r in enumerate(response):
        print(i, r)

    return response


def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = jumpy_pb2_grpc.JumiaStub(channel)
        # get_product(stub)
        # get_products(stub)
        # get_cheapest_product_per_stream(stub)
        get_cheapest_product_per_message(stub)


if __name__ == "__main__":
    run()