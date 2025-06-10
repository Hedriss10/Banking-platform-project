class Pagination:
    def pagination(
        self,
        current_page=1,
        rows_per_page=10,
        sort_by="",
        order_by="",
        filter_by="",
        filter_value="",
    ):
        return {
            "offset": current_page * rows_per_page - rows_per_page,
            "limit": rows_per_page,
            "sort_by": sort_by,
            "order_by": order_by,
            "filter_by": filter_by,
            "filter_value": filter_value,
        }

    def metadata(
        self,
        current_page=None,
        total_pages=None,
        total_rows=None,
        rows_per_page=None,
        sort_by=None,
        order_by=None,
        filter_by=None,
        filter_value=None,
        total=None,
    ):
        return {
            "current_page": current_page,
            "total_pages": total_pages,
            "total_rows": total_rows,
            "rows_per_page": rows_per_page,
            "sort_by": sort_by,
            "order_by": order_by,
            "filter_by": filter_by,
            "filter_value": filter_value,
            "total": total,
        }
