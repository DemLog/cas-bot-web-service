from enum import StrEnum
from typing import Optional

from pydantic import conint, Field

from shared.schemas.base import TunedModel


class CustomersForAllCategoriesBaseAnalysis(TunedModel):
    ru_category_1: str = Field(..., description="Title of the first level category in russian")
    href_category_1: str = Field(..., description="Href to the first level category")
    ru_category_2: str = Field(..., description="Title of the second level category in russian")
    href_category_2: str = Field(..., description="Href to the second level category")
    ru_category_3: Optional[str] = Field(..., description="Title of the third level category in russian")
    href_category_3: Optional[str] = Field(..., description="Href to the third level category")
    ru_category_4: Optional[str] = Field(..., description="Title of the fourth level category in russian")
    href_category_4: Optional[str] = Field(..., description="Href to the fourth level category")
    product_fullname: str = Field(..., description="The full name of the analysis product")
    customers_count: conint(ge=0) = Field(..., description="Count of customers of the product")

    class Config:
        title = "Analysis customers across all categories"


class CustomersForAllCategoriesAnalysis(CustomersForAllCategoriesBaseAnalysis):
    analysis_value_avg: float = Field(..., description="Average value of the analysis for the customer across all reviews / comments")

    class Config:
        title = "Analysis value customers across all categories"


class GroupRegionallyAllCustomerAnalysis(TunedModel):
    country_ru: Optional[str] = Field(..., description="Customer country in russian")
    country_en: Optional[str] = Field(..., description="Customer country in english")
    city_ru: Optional[str] = Field(..., description="Customer city in russian")
    city_en: Optional[str] = Field(..., description="Customer city in english")
    latitude: float = Field(..., description="Latitude of the customer region")
    longitude: float = Field(..., description="Longitude of the customer region")
    object_count: conint(ge=0) = Field(..., description="Count of reviews / comments on the analysis by region")
    analysis_value_avg: float = Field(..., description="Average value of the analysis for the customer across all reviews / comments")

    class Config:
        title = "Customer analysis values by region"


class CustomerReputationAnalysisValue(TunedModel):
    reputation: int = Field(..., description="Customer reputation value")
    analysis_value: float = Field(..., description="Customer analysis value")

    class Config:
        title = "Value of customer analysis mapped to customer reputation"


class AnalysisObjectType(StrEnum):
    reviewers = "reviewers"
    commentators = "commentators"


class AnalysisPrepareSimilarityObjectType(StrEnum):
    products = "products"
    customers = "customers"


class SentimentAnalysisType(StrEnum):
    region = "region"
    category = "category"


class SimilarityAnalysisType(StrEnum):
    category = "category"
    reputation = "reputation"


class AnalysisType(StrEnum):
    interest_reviewers = "interest_reviewers"
    interest_commentators = "interest_commentators"
    sentiment_category_reviewers = "sentiment_category_reviewers"
    sentiment_category_commentators = "sentiment_category_commentators"
    sentiment_region_reviewers = "sentiment_region_reviewers"
    sentiment_region_commentators = "sentiment_region_commentators"
    similarity_reputation_reviewers = "similarity_reputation_reviewers"
    similarity_reputation_commentators = "similarity_reputation_commentators"
    similarity_category_reviewers = "similarity_category_reviewers"
    similarity_category_commentators = "similarity_category_commentators"
