import requests
import re
from bs4 import BeautifulSoup as bso


class JumiaProduct(object):
    """
    This class parses the products section pages of jumia.com.ng,
    then it extracts some data such as the product names, prices, ratings, number of rated sales,
    links.
    """

    def __init__(self, category_link, page_num):

        if requests.get(category_link).status_code != 200:
            raise ConnectionError("This link is invalid")

        if (".html" or "?") in category_link:
            raise Exception("This link doesn't lead to a Jumia category")

        if type(page_num) != int:
            raise TypeError("page_num should be an integer")

        self.category_link = category_link
        self.page_num = page_num
        self.page = self._get_page()

    def _get_page(self):
        """

        This method is used to get the html pages of products from
        the section link provided.

        It returns a list of the html pages.
        """
        address_extension = "?page={}".format(self.page_num)
        full_address = self.category_link + address_extension
        html_request = requests.get(full_address)
        html_content = html_request.content
        return bso(html_content, "html.parser").find("section", {"class": "card -fh"})

    def get_data(self, index=None):
        """
        This method is used to get the products data.
        """
        class_value = re.compile(r"(?:prd _fb col c-prd$)")
        products = self.page.find_all("article", {"class": class_value})

        data = []
        if index:
            products = [products[index]]

        for product in products:
            link = "https://www.jumia.com.ng{}".format(product.find("a")["href"])
            name = product.find("h3", {"class": "name"}).text
            price = product.find("div", {"class": "prc"}).text
            price = price.split(' ')[1] + " NGN"

            review_div = product.find("div", {"class": "rev"})
            if not review_div:
                rating = "No Rating"
                rated_sales = "No Rating"
            else:
                rating_tag = review_div.find("div", {"class": "in"})["style"]
                rating_re = re.compile(r"[0-9]+")
                rating = format(int(rating_re.findall(rating_tag)[0]) / 100 * 5, '.2f')

                rated_sales_re = re.compile(r"\(([0-9]+)\)")
                sales_count = rated_sales_re.search(review_div.text)
                rated_sales = sales_count.group(1)
            data.append({
                "link": link,
                "name": name,
                "price": price,
                "rating": rating,
                "rated_sales": rated_sales
            })

        return data[0] if index else data
