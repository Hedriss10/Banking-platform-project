from src.db.pg import PgAdmin
from src.service.response import Response
from src.utils.pagination import Pagination
from src.models.hourspoint import HourspointModel
from src.utils.log import setup_logger

logger = setup_logger(__name__)

class HourspointCore:
    
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.models = HourspointModel(user_id=user_id)
        self.pg = PgAdmin()
    
    def list_employee(self, data: dict):
        current_page, rows_per_page = int(data.get("current_page", 1)), int(data.get("rows_per_page", 10))

        if current_page < 1:
            current_page = 1
        if rows_per_page < 1:
            rows_per_page = 1

        pagination = Pagination().pagination(
            current_page=current_page,
            rows_per_page=rows_per_page,
            sort_by=data.get("sort_by", ""),
            order_by=data.get("order_by", ""),
            filter_by=data.get("filter_by", "")
        )

        employee = self.pg.fetch_to_dict(query=self.models.list_employee(pagination=pagination))
        
        if not employee:
            logger.warning(f"Employee List Not Found.")
            return Response().response(status_code=404, error=True, message_id="employee_list_not_found", exception="Not found", data=employee)

        metadata = Pagination().metadata(
            current_page=current_page,
            rows_per_page=rows_per_page,
            sort_by=pagination["sort_by"],
            order_by=pagination["order_by"],
            filter_by=pagination["filter_by"]
        )
        return Response().response(status_code=200, message_id="employee_list_successful", data=employee,  metadata=metadata)
        
    def edit_employee(self, id: int, data: dict):
        try:
            if not id:
                logger.warning(f"Id is required.")
                return Response().response(status_code=401, error=True, message_id="id_is_required", exception="Id employee is required.")
            
            self.pg.execute_query(query=self.models.edit_employee(data=data, id=id))
            self.pg.commit()
            return Response().response(status_code=200, error=False, message_id="employee_update_successful")
        except Exception as e:
            logger.error(f"Error processing holiday {e}", exc_info=True)
            return Response().response(status_code=400, message_id="error_employee_update", error=True, exception="Bad Request")
       
    def delete_employee(self, id: int):
        try:
            if not id:
                logger.warning(f"Id is required.")
                return Response().response(status_code=401, error=True, message_id="id_is_required", exception="Id employee is required.")
            
            self.pg.execute_query(query=self.models.delete_employee(id=id))
            self.pg.commit()
            return Response().response(status_code=200, error=False, message_id="employee_delete_successful")
        except Exception as e:
            logger.error(f"Error processing holiday {e}", exc_info=True)
            return Response().response(status_code=400, message_id="error_employee_delete", error=True, exception="Bad Request")
       
    def add_holiday(self, data: dict):
        try:
            if not data.get("data"):
                logger.warning(f"Data is required")
                return Response().response(status_code=401, error=True, message_id="data_is_required", exception="Data Name Is Required")
            
            holiday = self.pg.execute_query(query=self.models.add_holiday(data=data))
            self.pg.commit()
            return Response().response(status_code=200, error=False, message_id="holiday_add_successful")
        
        except Exception as e:
            logger.error(f"Error processing holiday {e}", exc_info=True)
            return Response().response(status_code=400, error=True, message_id="holiday_error", exception="Error Add Holiday", traceback=str(e))
    
    def list_holiday(self, data: dict):
        current_page, rows_per_page = int(data.get("current_page", 1)), int(data.get("rows_per_page", 10))
        
        if current_page < 1:
            current_page = 1
        if rows_per_page < 1:
            rows_per_page = 1

        pagination = Pagination().pagination(
            current_page=current_page,
            rows_per_page=rows_per_page,
            sort_by=data.get("sort_by", ""),
            order_by=data.get("order_by", ""),
            filter_by=data.get("filter_by", "")
        )

        holiday = self.pg.fetch_to_dict(query=self.models.list_holiday(pagination=pagination))

        if not holiday:
            logger.warning(f"holiday List Not Found.")
            return Response().response(status_code=404, error=True, message_id="holiday_list_not_found", exception="Not found", data=holiday)

        metadata = Pagination().metadata(
            current_page=current_page,
            rows_per_page=rows_per_page,
            sort_by=pagination["sort_by"],
            order_by=pagination["order_by"],
            filter_by=pagination["filter_by"]
        )
        return Response().response(status_code=200, message_id="holiday_list_successful", data=holiday,  metadata=metadata)
    
    def delete_holiday(self, id: int):
        try:
            if not id:
                logger.warning(f"Id is required.")
                return Response().response(status_code=401, error=True, message_id="id_is_required", exception="Id Holiday is required.")
            
            self.pg.execute_query(query=self.models.delete_holiday(id=id))
            self.pg.commit()
            return Response().response(status_code=200, error=False, message_id="holiday_delete_successful")
        except Exception as e:
            logger.error(f"Error processing holiday {e}", exc_info=True)
            return Response().response(status_code=400, message_id="error_holiday_delete", error=True, exception="Bad Request")
    
    def add_absence(self, data: dict):
        try:
            if not data.get("data") and data.get("descricao") and data.get("justificavel"):
                logger.warning(f"Data and description and justify")
                return Response().response(status_code=401, error=True, message_id="data_and_description_justify_is_required", exception="Data, Description, is Required")
            
            absence = self.pg.fetch_to_dict(query=self.models.add_absence_resource(decription=data.get("descricao"), justified=data.get("justificavel")))
                        
            if absence:
               self.pg.execute_query(query=self.models.add_absence(motivo_id=absence[0]["id"], data=data, employee_id=data.get("employee_id")))
               self.pg.commit()
               return Response().response(status_code=200, error=False, message_id="absence_add_successful")                
            
            else:
                logger
                return Response().response(status_code=400, error=False, message_id="absence_error", data=absence)
             
        except Exception as e:
            logger.error(f"Error processing holiday {e}", exc_info=True)
            return Response().response(status_code=400, error=True, message_id="absence_error", exception="Error Add Abscence", traceback=str(e))
        
    def list_absence_resource(self, data: dict):
        current_page, rows_per_page = int(data.get("current_page", 1)), int(data.get("rows_per_page", 10))
        
        if current_page < 1:
            current_page = 1
        if rows_per_page < 1:
            rows_per_page = 1

        pagination = Pagination().pagination(
            current_page=current_page,
            rows_per_page=rows_per_page,
            sort_by=data.get("sort_by", ""),
            order_by=data.get("order_by", ""),
            filter_by=data.get("filter_by", "")
        )

        absence = self.pg.fetch_to_dict(query=self.models.list_absence(pagination=pagination))

        if not absence:
            logger.warning(f"Absence List Not Found.")
            return Response().response(status_code=404, error=True, message_id="absence_list_not_found", exception="Not found", data=absence)

        metadata = Pagination().metadata(
            current_page=current_page,
            rows_per_page=rows_per_page,
            sort_by=pagination["sort_by"],
            order_by=pagination["order_by"],
            filter_by=pagination["filter_by"]
        )
        return Response().response(status_code=200, message_id="absence_list_successful", data=absence,  metadata=metadata) 
    
    def edit_absence(self, id: int, data: dict):
        try:
            if not id:
                logger.warning(f"Id is required.")
                return Response().response(status_code=401, error=True, message_id="id_is_required", exception="Id Absence is required.")
            
            self.pg.execute_query(query=self.models.edit_absence_reason(id=id, description=data.get("descricao"), justified=data.get("justificavel")))
            self.pg.commit()
            return Response().response(status_code=200, error=False, message_id="absence_delete_successful")
        except Exception as e:
            logger.error(f"Error processing holiday {e}", exc_info=True)
            return Response().response(status_code=400, message_id="error_absence_edit", error=True, exception="Bad Request")
        
    def add_vacation(self, data: dict):
        try:
            if not data.get("employee_id"):
                logger.warning(f"Name is required")
                return Response().response(status_code=401, error=True, message_id="employee_is_required", exception="Employee_id Is Required")
            
            self.pg.execute_query(query=self.models.add_vacation(data=data))
            self.pg.commit()
            return Response().response(status_code=200, error=False, message_id="vacation_add_successful")
        except Exception as e:
            logger.error(f"Error processing holiday {e}", exc_info=True)
            return Response().response(status_code=400, error=True, message_id="vacation_error", exception="Error ad Vacation", traceback=str(e))
              
    def edit_vacation(self, id: int, data: dict):
        try:
            if not id:
                logger.warning(f"Id is required")
                return Response().response(status_code=401, error=True, message_id="id_is_required", exception="Id Is Required")
            
            self.pg.execute_query(query=self.models.edit_vacation(id=id, data=data))
            self.pg.commit()
            return Response().response(status_code=200, error=False, message_id="vacation_edit_successful")
        except Exception as e:
            logger.error(f"Error processing holiday {e}", exc_info=True)
            return Response().response(status_code=400, error=True, message_id="vacation_error", exception="Error ad Vacation", traceback=str(e))

    def delete_vaction(self, id: int):
        try:
            if not id:
                logger.warning(f"Id is required")
                return Response().response(status_code=401, error=True, message_id="id_is_required", exception="Id Is Required")
            
            self.pg.execute_query(query=self.models.delete_vacation(id=id))
            self.pg.commit()
            return Response().response(status_code=200, error=False, message_id="vacation_delete_successful")
        except Exception as e:
            logger.error(f"Error processing holiday {e}", exc_info=True)
            return Response().response(status_code=400, error=True, message_id="vacation_error", exception="Error ad Vacation", traceback=str(e))
        
    def add_time_point(self, data: dict):
        try:
            if not data.get("employee_id"):
                logger.warning(f"Name is required")
                return Response().response(status_code=401, error=True, message_id="employee_is_required", exception="Employee_id Is Required")
            
            self.pg.execute_query(query=self.models.add_time_point(data=data))
            self.pg.commit()
            return Response().response(status_code=200, error=False, message_id="time_point_add_successful")
        except Exception as e:
            logger.error(f"Error processing holiday {e}", exc_info=True)
            return Response().response(status_code=400, error=True, message_id="time_point_error", exception="Error ad Timepoint", traceback=str(e))
        
    def add_justification_for_delay(self, data: dict):
        try:
            if not data.get("employee_id"):
                logger.warning(f"Name is required")
                return Response().response(status_code=401, error=True, message_id="employee_is_required", exception="Employee_id Is Required")
            
            self.pg.execute_query(query=self.models.add_justification_for_delay(data=data))
            self.pg.commit()
            return Response().response(status_code=200, error=False, message_id="add_justification_for_delay_successful")
        except Exception as e:
            logger.error(f"Error processing holiday {e}", exc_info=True)
            return Response().response(status_code=400, error=True, message_id="add_justification_for_delay_error", exception="Error ad add_justification_for_delay", traceback=str(e))
        
    def list_day_offs(self, data: dict):
        current_page, rows_per_page = int(data.get("current_page", 1)), int(data.get("rows_per_page", 10))

        if current_page < 1:
            current_page = 1
        if rows_per_page < 1:
            rows_per_page = 1

        pagination = Pagination().pagination(
            current_page=current_page,
            rows_per_page=rows_per_page,
            sort_by=data.get("sort_by", ""),
            order_by=data.get("order_by", ""),
            filter_by=data.get("filter_by", "")
        )

        list_day_offs = self.pg.fetch_to_dict(query=self.models.list_day_offs(pagination=pagination))
        
        if not list_day_offs:
            logger.warning(f"List_day_offs List Not Found.")
            return Response().response(status_code=404, error=True, message_id="list_day_offs_not_found", exception="Not found", data=list_day_offs)

        metadata = Pagination().metadata(
            current_page=current_page,
            rows_per_page=rows_per_page,
            sort_by=pagination["sort_by"],
            order_by=pagination["order_by"],
            filter_by=pagination["filter_by"]
        )
        return Response().response(status_code=200, message_id="list_day_offs_successful", data=list_day_offs,  metadata=metadata)
    
    def list_works_hours_overtime(self, data: dict):
        current_page, rows_per_page = int(data.get("current_page", 1)), int(data.get("rows_per_page", 10))

        if current_page < 1:
            current_page = 1
        if rows_per_page < 1:
            rows_per_page = 1

        pagination = Pagination().pagination(
            current_page=current_page,
            rows_per_page=rows_per_page,
            sort_by=data.get("sort_by", ""),
            order_by=data.get("order_by", ""),
            filter_by=data.get("filter_by", "")
        )

        list_works_hours_overtime = self.pg.fetch_to_dict(query=self.models.list_works_hours_overtime(pagination=pagination))
        
        if not list_works_hours_overtime:
            logger.warning(f"list_works_hours_overtime List Not Found.")
            return Response().response(status_code=404, error=True, message_id="list_works_hours_overtime_not_found", exception="Not found", data=list_works_hours_overtime)

        metadata = Pagination().metadata(
            current_page=current_page,
            rows_per_page=rows_per_page,
            sort_by=pagination["sort_by"],
            order_by=pagination["order_by"],
            filter_by=pagination["filter_by"]
        )
        return Response().response(status_code=200, message_id="list_works_hours_overtime_successful", data=list_works_hours_overtime,  metadata=metadata)
    
    def list_works_delay(self, data: dict):
        current_page, rows_per_page = int(data.get("current_page", 1)), int(data.get("rows_per_page", 10))

        if current_page < 1:
            current_page = 1
        if rows_per_page < 1:
            rows_per_page = 1

        pagination = Pagination().pagination(
            current_page=current_page,
            rows_per_page=rows_per_page,
            sort_by=data.get("sort_by", ""),
            order_by=data.get("order_by", ""),
            filter_by=data.get("filter_by", "")
        )

        list_works_delay = self.pg.fetch_to_dict(query=self.models.list_works_delay(pagination=pagination))
        
        if not list_works_delay:
            logger.warning(f"list_works_delay List Not Found.")
            return Response().response(status_code=404, error=True, message_id="list_works_delay_not_found", exception="Not found", data=list_works_delay)

        metadata = Pagination().metadata(
            current_page=current_page,
            rows_per_page=rows_per_page,
            sort_by=pagination["sort_by"],
            order_by=pagination["order_by"],
            filter_by=pagination["filter_by"]
        )
        return Response().response(status_code=200, message_id="list_works_delay_successful", data=list_works_delay,  metadata=metadata)

    def list_vocation_apply(self, data: dict):
        current_page, rows_per_page = int(data.get("current_page", 1)), int(data.get("rows_per_page", 10))

        if current_page < 1:
            current_page = 1
        if rows_per_page < 1:
            rows_per_page = 1

        pagination = Pagination().pagination(
            current_page=current_page,
            rows_per_page=rows_per_page,
            sort_by=data.get("sort_by", ""),
            order_by=data.get("order_by", ""),
            filter_by=data.get("filter_by", "")
        )

        list_vocation_apply = self.pg.fetch_to_dict(query=self.models.list_vocation_apply(pagination=pagination))
        
        if not list_vocation_apply:
            logger.warning(f"list_vocation_apply List Not Found.")
            return Response().response(status_code=404, error=True, message_id="list_vocation_apply_not_found", exception="Not found", data=list_vocation_apply)

        metadata = Pagination().metadata(
            current_page=current_page,
            rows_per_page=rows_per_page,
            sort_by=pagination["sort_by"],
            order_by=pagination["order_by"],
            filter_by=pagination["filter_by"]
        )
        return Response().response(status_code=200, message_id="list_vocation_apply_successful", data=list_vocation_apply,  metadata=metadata)
    
    def list_ranking_user_delayed_works_employess(self, data: dict):
        current_page, rows_per_page = int(data.get("current_page", 1)), int(data.get("rows_per_page", 10))

        if current_page < 1:
            current_page = 1
        if rows_per_page < 1:
            rows_per_page = 1

        pagination = Pagination().pagination(
            current_page=current_page,
            rows_per_page=rows_per_page,
            sort_by=data.get("sort_by", ""),
            order_by=data.get("order_by", ""),
            filter_by=data.get("filter_by", "")
        )

        list_ranking_user_delayed_works_employess = self.pg.fetch_to_dict(query=self.models.list_ranking_user_delayed_works_employess(pagination=pagination))
        
        if not list_ranking_user_delayed_works_employess:
            logger.warning(f"list_ranking_user_delayed_works_employess List Not Found.")
            return Response().response(status_code=404, error=True, message_id="list_ranking_user_delayed_works_employess_not_found", exception="Not found", data=list_ranking_user_delayed_works_employess)

        metadata = Pagination().metadata(
            current_page=current_page,
            rows_per_page=rows_per_page,
            sort_by=pagination["sort_by"],
            order_by=pagination["order_by"],
            filter_by=pagination["filter_by"]
        )
        return Response().response(status_code=200, message_id="list_ranking_user_delayed_works_employess_successful", data=list_ranking_user_delayed_works_employess,  metadata=metadata)