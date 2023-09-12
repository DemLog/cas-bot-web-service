import io
import json
import os
from pathlib import Path
from typing import Any, List

import pandas as pd
import plotly.express as px
import plotly.io as pio

from app.core.schemas import ProductSearch


class AnalysisService:
    def get_product_fake(self) -> List:
        with open(str(Path(__file__).parent.parent) + os.sep + "core" + os.sep + "data" + os.sep + "fake_products.json",
                  'r', encoding='utf-8') as fp:
            data_products = json.load(fp)
            return data_products["product"]

    def get_products_search(self, product_search: ProductSearch) -> [Any]:
        data = self.get_product_fake()
        for product in data:
            if product_search.text.lower() in product["key_words"]:
                return product["data"]
        return []

    def get_product_id(self, product_id: str) -> Any:
        data = self.get_product_fake()
        for category in data:
            for product in category["data"]:
                if product_id == product["id"]:
                    return product
        return None

    def get_analysis_interests_comments(self, data) -> Any:
        fig_comment_cat_all = px.treemap(pd.DataFrame(data),
                                         values='count',
                                         path=['ru_category_1', 'ru_category_2', 'ru_category_3', 'ru_category_4',
                                               'fullname'])
        fig_comment_cat_all.update_traces(root_color='lightgrey')

        buffer = io.BytesIO()
        fig_comment_cat_all.write_image(buffer, format="png")
        buffer.seek(0)

        return buffer

    def get_analysis_interests_reviews(self, data) -> Any:
        pass

    def get_analysis_sentiments_comments_category(self, data) -> Any:
        pass

    def get_analysis_sentiments_comments_region(self, data) -> Any:
        pass

    def get_analysis_sentiments_reviews_category(self, data) -> Any:
        pass

    def get_analysis_sentiments_reviews_region(self, data) -> Any:
        pass

    def get_analysis_similarity_comments(self, data) -> Any:
        pass

    def get_analysis_similarity_reviews(self, data) -> Any:
        pass


analysis_service = AnalysisService()
