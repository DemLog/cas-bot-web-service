base_responses = {
    400: {"description": "Bad Request"},
    401: {"description": "Unauthorized"},
    404: {"description": "Not Found"},
    422: {"description": "Validation Error"},
    500: {"description": "Internal Server Error"}
}

general_responses = {
    **base_responses,
    200: {
        "content": {
            "application/json": {
                "example": {"message": "success"}
            }
        },
    }
}

single_users_responses = {
    **base_responses,
    200: {
        "content": {
            "application/json": {
                "example": {
                    "id": 0,
                    "first_name": "string",
                    "last_name": "string",
                    "username": "string",
                    "role": "string",
                    "tokens": 0,
                    "is_active": True,
                    "is_accept_terms": True,
                    "created_profile": "string"
                }
            }
        },
    }
}

all_users_responses = {
    **base_responses,
    200: {
        "content": {
            "application/json": {
                "example": [{
                    "id": 0,
                    "first_name": "string",
                    "last_name": "string",
                    "username": "string",
                    "role": "string",
                    "tokens": 0,
                    "is_active": True,
                    "is_accept_terms": True,
                    "created_profile": "string"
                }]
            }
        },
    }
}

all_histories_responses = {
    **base_responses,
    200: {
        "content": {
            "application/json": {
                "example": [{
                    "id": 0,
                    "title": "string",
                    "date": "string",
                    "url": "string",
                    "user_id": 0
                }]
            }
        },
    }
}

search_products_responses = {
    **base_responses,
    200: {
        "content": {
            "application/json": {
                "example": [{
                    "id": "string",
                    "title": "string",
                    "categories": ["string"],
                    "url": "string",
                    "photo_url": "string",
                    "disabled": False
                }]
            }
        },
    }
}
