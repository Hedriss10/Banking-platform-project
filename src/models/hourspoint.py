
class HourspointModel:
    
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        
    def list_employee(self, pagination: dict):
        """
            Employee list filtered by deleted field equal to false.
        Args:
            pagination (dict): _description_
        """
        query_filter = ""
        if pagination["filter_by"]:
            query_filter = f"""AND (unaccent(u.cpf) ILIKE unaccent('%{pagination["filter_by"]}%'))"""
        
        query_order_by = ""
        if pagination["sort_by"] and pagination["order_by"]:
            query_order_by = f"""ORDER BY b.{pagination["order_by"]} {pagination["sort_by"]}"""
    
        query = f"""
            SELECT 
                el.id AS id_employee,
                u.id AS id_user,
                el.numero_pis,
                el.matricula,
                el.empresa,
                el.situacao_cadastro,
                el.carga_horaria_semanal,
                u.username,
                u.cpf,
                u.typecontract
            FROM employee el
            LEFT JOIN public.user u on u.id = el.user_id
            WHERE el.is_deleted=false {query_filter}
            ORDER BY id_employee
            OFFSET {pagination["offset"]} LIMIT {pagination["limit"]};
        """
        return query
        
    def add_holiday(self, data: dict):
        """
            add holiday associate employee id.
            columns: data, estado, descricao, tipo, employee_id, is_deleted
        Args:
            data (dict): _description_
        """
        query = f"""
            INSERT INTO holiday (data, estado, descricao, tipo, employee_id, is_deleted) 
            values ('{data.get("data")}', '{data.get("estado")}', '{data.get('descricao')}', '{data.get("tipo")}', {data.get("employee_id")}, false);
        """
        return query
    
    def list_holiday(self, pagination: dict):
        """
            list holiday associate with employee intersects with users.
        Args:
            pagination (dict): _description_
        """
        query_filter = ""
        if pagination["filter_by"]:
            query_filter = f"""AND (unaccent(username) ILIKE unaccent('%{pagination["filter_by"]}%'))"""
        
        query_order_by = ""
        if pagination["sort_by"] and pagination["order_by"]:
            query_order_by = f"""ORDER BY b.{pagination["order_by"]} {pagination["sort_by"]}"""
            
        query = f"""
            SELECT
                h.id,
                e.user_id AS id_user,
                e.id AS id_employee,
                initcap(trim(u.username)) AS username,
                initcap(trim(h.descricao)) AS descricao,
                h.estado,
                TO_CHAR(h.data, 'DD-MM-YYYY') AS data
            from 
                employee e 
                INNER JOIN holiday h on h.employee_id = e.id 
                LEFT JOIN public.user u on u.id = e.user_id
                WHERE h.is_deleted = false {query_filter}
                ORDER BY id_employee
            OFFSET {pagination["offset"]} LIMIT {pagination["limit"]};
        """
        return query
    
    def delete_holiday(self, id: int):
        query = f"""
            update holiday
            set
                updated_at = now()
                updated_by = {self.user_id}
            where id = {id};
        """
        return query
    
    def add_absence_resource(self, decription: str, justified: bool):
        """
            Add absence resource -> descricao, justificavel, is_deleted
            returning id 
        Args:
            data (dict): _description_
            id (int): id_absence_resource
        """
        query = f"""
            INSERT INTO absence_reason(descricao, justificavel, is_deleted) 
            VALUES ('{decription}', {justified}, false)
            RETURNING id;
        """
        return query
    
    def add_absence(self, motivo_id: int, employee_id: int, data: dict):
        """
            Add absence assciate with `add_absence_resource`
            columns: employee_id, data, motivo_id, justificativa, is_deleted
        Args:
            id (int): add_absence_resource
            employee_id (int): employee_id
            data (dict): _description_
        """
        query = f"""
            INSERT INTO absence (employee_id, data, motivo_id, justificativa, is_deleted)
            VALUES ({employee_id}, '{data.get("data")}', {motivo_id}, '{data.get("justificativa")}', false);
        """
        return query
    
    def edit_absence_reason(self, id: int, description: str, justified: bool):
        """_summary_
            Update absence_reason filter by id 
        Args:
            id (int): id absence_reason
        """
        query = f"""
            UPDATE absence_reason
            set
                descricao = '{description}',
                justificavel = {justified},
                updated_at = now(),
                updated_by = {self.user_id}
            WHERE id = {id};
        """
        return query
    
    def list_absence(self, pagination: dict):
        """
            listing of justified and unjustified absences by users
        Args:
            pagination (dict): _description_
        """
        query_filter = ""
        if pagination["filter_by"]:
            query_filter = f"""AND (unaccent(username) ILIKE unaccent('%{pagination["filter_by"]}%'))"""
        
        query_order_by = ""
        if pagination["sort_by"] and pagination["order_by"]:
            query_order_by = f"""ORDER BY b.{pagination["order_by"]} {pagination["sort_by"]}"""
        
        query = f"""
            select
                abr.id as id_absence_reason,
                u.id as id_user,
                initcap(trim(u.username)) as username,
                initcap(trim(ab.justificativa)) as justificativa,
                initcap(trim(abr.descricao)) as descricao,
                abr.justificavel,
                ab.data
            from employee el
            INNER JOIN public.user u ON u.id = el.user_id
            INNER JOIN absence ab ON ab.employee_id= el.id
            INNER JOIN absence_reason abr ON abr.id = ab.motivo_id
            WHERE el.is_deleted = false {query_filter}
            ORDER BY el.id
            OFFSET {pagination["offset"]} LIMIT {pagination["limit"]};
        """
        return query
    
    def add_vacation(self, data: dict):
        """
            columns: employee_id, data_inicio, data_fim, aprovado, user_id, is_deleted
        Args:
            data (dict): _description_
        """
        
        query = f"""
            INSERT INTO vacation (employee_id, data_inicio, data_fim, aprovado, user_id, is_deleted) 
            VALUES ({data.get("employee_id")}, '{data.get("data_inicio")}', '{data.get("data_fim")}', {data.get("aprovado")}, {self.user_id}, false);
        """
        return query
    
    def edit_vacation(self, id: int, data: dict):
        """ 
            Update vacation filter by id 

        Args:
            id (int): _description_
            data (dict): _description_
        """
        # iterating over the pagination collecting the items that are present and creating a set within the database
        set_clasule = []
        for key, value in data.items():
            if value is not None:                    
                set_clasule.append(f""" {key} = '{value}' """)
        
        set_clause_str = ", ".join(set_clasule)
        
        query = f"""
            update vacation
            set
                {set_clause_str},
                updated_at = now(),
                updated_by = {self.user_id}
            where id = {id};
        """
        return query
    
    def delete_vacation(self, id: int):
        """
            Delete vacation filter by id

        Args:
            id (int): _description_
        """
        query = f"""
            update vacation
            set
                is_deleted=true
            where id = {id};
        """
        return query
    
    def add_time_point(self, data: dict):
        """
            columns: employee_id, data, entrada, saida, entrada_almoco, saida_almoco, entrada_lanche, saida_lanche, user_id, is_deleted
        Args:
            data (dict): returning register point with users asscoiate employee
        """
        query = f"""
            INSERT INTO time_point (employee_id, data, entrada, saida, entrada_almoco, saida_almoco, entrada_lanche, saida_lanche, user_id, is_deleted) 
            VALUES  ({data.get("employee_id")}, '{data.get("data")}', '{data.get("entrada")}', '{data.get("saida")}', '{data.get("entrada_almoco")}', '{data.get("saida_almoco")}', '{data.get("entrada_lanche")}', '{data.get("saida_lanche")}', {self.user_id}, false);
        """
        return query
    
    def add_justification_for_delay(self, data: dict):
        """
            columns: employee_id, data, justificativa, user_id, is_deleted

        Args:
            data (dict): _description_
        """
        query = f"""
            INSERT INTO time_point(employee_id, data, justificativa, user_id, is_deleted) 
            VALUES ({data.get("employee_id")}, now(), '{data.get("justificativa")}', {self.user_id}, false);
        """
        return query
    
    def list_day_offs(self, pagination: dict):
        """
            quantitative report sum of justified or unjustified absences managed by the user manager
        Args:
            pagination (dict): list day offs if justified or unjustified
        """
        query_filter = ""
        if pagination["filter_by"]:
            query_filter = f"""AND (unaccent(username) ILIKE unaccent('%{pagination["filter_by"]}%'))"""
        
        query_order_by = ""
        if pagination["sort_by"] and pagination["order_by"]:
            query_order_by = f"""ORDER BY b.{pagination["order_by"]} {pagination["sort_by"]}"""
            
        query = f"""
            SELECT 
                e.id AS employee_id,
                u.username,
                u.typecontract,
                COUNT(a.id) AS total_absences,
                SUM(CASE WHEN ar.justificavel THEN 1 ELSE 0 END) AS justificadas,
                SUM(CASE WHEN NOT ar.justificavel THEN 1 ELSE 0 END) AS nao_justificadas
            FROM 
                public.employee e
                LEFT JOIN public.user u on u.id = e.user_id
                LEFT JOIN public.absence a ON a.employee_id = e.id
                LEFT JOIN public.absence_reason ar ON a.motivo_id = ar.id
            WHERE e.is_deleted = false {query_filter}
            GROUP BY e.id, u.username, u.typecontract
            OFFSET {pagination["offset"]} LIMIT {pagination["limit"]};
        """
        return query
    
    def list_works_hours_overtime(self, pagination: dict):
        """
            List of overtime hours within the CLT rule: Up to 2 extra hours per day are called 50% overtime and from the 3rd hour onwards they are called 100% overtime
        Args:
            pagination (dict): _description_
        """
        query_filter = ""
        if pagination["filter_by"]:
            query_filter = f"""AND (unaccent(co.username) ILIKE unaccent('%{pagination["filter_by"]}%'))"""
        
        query_order_by = ""
        if pagination["sort_by"] and pagination["order_by"]:
            query_order_by = f"""ORDER BY b.{pagination["order_by"]} {pagination["sort_by"]}"""
            
        query = f"""
            WITH work_hours AS (
                SELECT
                    e.id AS employee_id,
                    u.id AS id_user,
                    INITCAP(TRIM(u.username)) AS username,
                    u.typecontract,
                    t.data,
                    t.entrada,
                    t.entrada_almoco,
                    t.saida_almoco,
                    t.entrada_lanche,
                    t.saida_lanche,
                    t.saida,
                    -- Calcular total trabalhado descontando almoço e lanche
                    EXTRACT(EPOCH FROM (t.saida - t.entrada)) / 3600 
                    - CASE 
                        WHEN t.entrada_almoco IS NOT NULL AND t.saida_almoco IS NOT NULL THEN
                            EXTRACT(EPOCH FROM (t.saida_almoco - t.entrada_almoco)) / 3600
                        ELSE 0
                    END
                    - CASE 
                        WHEN t.entrada_lanche IS NOT NULL AND t.saida_lanche IS NOT NULL THEN
                            EXTRACT(EPOCH FROM (t.saida_lanche - t.entrada_lanche)) / 3600
                        ELSE 0
                    END AS total_hours_worked,
                    -- Calcular horas extras
                    CASE 
                        WHEN EXTRACT(EPOCH FROM (t.saida - t.entrada)) / 3600 
                            - CASE 
                                WHEN t.entrada_almoco IS NOT NULL AND t.saida_almoco IS NOT NULL THEN
                                    EXTRACT(EPOCH FROM (t.saida_almoco - t.entrada_almoco)) / 3600
                                ELSE 0
                            END
                            - CASE 
                                WHEN t.entrada_lanche IS NOT NULL AND t.saida_lanche IS NOT NULL THEN
                                    EXTRACT(EPOCH FROM (t.saida_lanche - t.entrada_lanche)) / 3600
                                ELSE 0
                            END > 8.8 THEN
                            EXTRACT(EPOCH FROM (t.saida - t.entrada)) / 3600 
                            - CASE 
                                WHEN t.entrada_almoco IS NOT NULL AND t.saida_almoco IS NOT NULL THEN
                                    EXTRACT(EPOCH FROM (t.saida_almoco - t.entrada_almoco)) / 3600
                                ELSE 0
                            END
                            - CASE 
                                WHEN t.entrada_lanche IS NOT NULL AND t.saida_lanche IS NOT NULL THEN
                                    EXTRACT(EPOCH FROM (t.saida_lanche - t.entrada_lanche)) / 3600
                                ELSE 0
                            END
                            - 8.8
                        ELSE 0
                    END AS overtime_hours
                FROM 
                    employee e
                INNER JOIN 
                    public.time_point t ON t.employee_id = e.id
                LEFT JOIN 
                    public.user u ON u.id = e.user_id
                WHERE 
                    t.entrada IS NOT NULL AND t.saida IS NOT NULL
            ),
            calculated_overtime AS (
                SELECT 
                    employee_id,
                    id_user,
                    username,
                    typecontract,
                    data,
                    entrada,
                    entrada_almoco,
                    saida_almoco,
                    entrada_lanche,
                    saida_lanche,
                    saida,
                    total_hours_worked,
                    CASE 
                        WHEN overtime_hours <= 2 THEN overtime_hours
                        ELSE 2 
                    END AS overtime_50,
                    CASE 
                        WHEN overtime_hours > 2 THEN overtime_hours - 2 
                        ELSE 0 
                    END AS overtime_100
                FROM 
                    work_hours
            )
            SELECT 
                id_user,
                username,
                typecontract,
                TO_CHAR(data, 'DD-MM-YYYY') AS data,
                TO_CHAR(entrada, 'DD-MM-YYYY HH24:MI') AS entrada,
                TO_CHAR(entrada_almoco, 'DD-MM-YYYY HH24:MI') AS entrada_almoco,
                TO_CHAR(saida_almoco, 'DD-MM-YYYY HH24:MI') AS saida_almoco,
                TO_CHAR(entrada_lanche, 'DD-MM-YYYY HH24:MI') AS entrada_lanche,
                TO_CHAR(saida_lanche, 'DD-MM-YYYY HH24:MI') AS saida_lanche,
                TO_CHAR(saida, 'DD-MM-YYYY HH24:MI') AS saida,
                ROUND(total_hours_worked::numeric, 2) as total_hours_worked,
                ROUND(overtime_50::numeric, 2) AS "Horas Extras 50%",
                ROUND(overtime_100::numeric, 2) AS "Horas Extras 100%"
            FROM 
                calculated_overtime co
            {"WHERE" if query_filter else ""}
            ORDER BY username, data
            OFFSET {pagination["offset"]} LIMIT {pagination["limit"]};
        """
        return query
        
    def list_works_delay(self, pagination: dict):
        """_summary_

        Args:
            pagination (dict): _description_
        """
        query_filter = ""
        if pagination["filter_by"]:
            query_filter = f"""AND (unaccent(wk.username) ILIKE unaccent('%{pagination["filter_by"]}%'))"""
        
        query_order_by = ""
        if pagination["sort_by"] and pagination["order_by"]:
            query_order_by = f"""ORDER BY b.{pagination["order_by"]} {pagination["sort_by"]}"""
        
        query = f"""
            WITH work_hours AS (
                SELECT
                    e.id AS employee_id,
                    u.id AS id_user,
                    INITCAP(TRIM(u.username)) AS username,
                    u.typecontract,
                    t.data,
                    t.entrada,
                    t.entrada_almoco,
                    t.saida_almoco,
                    t.entrada_lanche,
                    t.saida_lanche,
                    t.saida,
                    EXTRACT(EPOCH FROM (t.saida - t.entrada)) / 3600 
                    - CASE 
                        WHEN t.entrada_almoco IS NOT NULL AND t.saida_almoco IS NOT NULL THEN
                            EXTRACT(EPOCH FROM (t.saida_almoco - t.entrada_almoco)) / 3600
                        ELSE 0
                    END
                    - CASE 
                        WHEN t.entrada_lanche IS NOT NULL AND t.saida_lanche IS NOT NULL THEN
                            EXTRACT(EPOCH FROM (t.saida_lanche - t.entrada_lanche)) / 3600
                        ELSE 0
                    END AS total_hours_worked,
                    CASE 
                        WHEN (EXTRACT(EPOCH FROM (t.saida - t.entrada)) / 3600 
                            - CASE 
                                WHEN t.entrada_almoco IS NOT NULL AND t.saida_almoco IS NOT NULL THEN
                                    EXTRACT(EPOCH FROM (t.saida_almoco - t.entrada_almoco)) / 3600
                                ELSE 0
                            END
                            - CASE 
                                WHEN t.entrada_lanche IS NOT NULL AND t.saida_lanche IS NOT NULL THEN
                                    EXTRACT(EPOCH FROM (t.saida_lanche - t.entrada_lanche)) / 3600
                                ELSE 0
                            END) < 8.8 THEN
                            (8.8 - (EXTRACT(EPOCH FROM (t.saida - t.entrada)) / 3600 
                            - CASE 
                                WHEN t.entrada_almoco IS NOT NULL AND t.saida_almoco IS NOT NULL THEN
                                    EXTRACT(EPOCH FROM (t.saida_almoco - t.entrada_almoco)) / 3600
                                ELSE 0
                            END
                            - CASE 
                                WHEN t.entrada_lanche IS NOT NULL AND t.saida_lanche IS NOT NULL THEN
                                    EXTRACT(EPOCH FROM (t.saida_lanche - t.entrada_lanche)) / 3600
                                ELSE 0
                            END)) 
                        ELSE 0
                    END AS atraso
                FROM 
                    employee e
                INNER JOIN 
                    public.time_point t ON t.employee_id = e.id
                LEFT JOIN 
                    public.user u ON u.id = e.user_id
                WHERE 
                    t.entrada IS NOT NULL AND t.saida IS NOT NULL
            )
            SELECT 
                id_user,
                username,
                typecontract,
                TO_CHAR(data, 'DD-MM-YYYY') AS data,
                TO_CHAR(entrada, 'DD-MM-YYYY HH24:MI') AS entrada,
                TO_CHAR(entrada_almoco, 'DD-MM-YYYY HH24:MI') AS entrada_almoco,
                TO_CHAR(saida_almoco, 'DD-MM-YYYY HH24:MI') AS saida_almoco,
                TO_CHAR(entrada_lanche, 'DD-MM-YYYY HH24:MI') AS entrada_lanche,
                TO_CHAR(saida_lanche, 'DD-MM-YYYY HH24:MI') AS saida_lanche,
                TO_CHAR(saida, 'DD-MM-YYYY HH24:MI') AS saida,
                ROUND(total_hours_worked::numeric, 2) as total_hours_worked,
                ROUND(atraso::numeric, 2) AS "Atraso (em horas)"
            FROM 
                work_hours wk
            {"WHERE" if query_filter else ""}
            ORDER BY username, data
            OFFSET {pagination["offset"]} LIMIT {pagination["limit"]};
        """
        return query
    
    def list_vocation_apply(self, pagination: dict):
        """
            report of approved and rejected vacations select
        Args:
            paginaton (dict): _description_
        """
        query_filter = ""
        if pagination["filter_by"]:
            query_filter = f"""AND (unaccent(username) ILIKE unaccent('%{pagination["filter_by"]}%'))"""
        
        query_order_by = ""
        if pagination["sort_by"] and pagination["order_by"]:
            query_order_by = f"""ORDER BY b.{pagination["order_by"]} {pagination["sort_by"]}"""
        
        query = f"""
            SELECT 
                v.id,
                u.id AS id_user,
                initcap(trim(u.username)) AS username,
                TO_CHAR(v.data_inicio, 'DD-MM-YYYY') AS data_inicio,
                TO_CHAR(v.data_fim, 'DD-MM-YYYY') AS data_fim,
                v.aprovado
            FROM 
                public.employee e
                INNER JOIN public.vacation v on v.employee_id = e.id
                LEFT JOIN public.user u on u.id = e.user_id
                WHERE e.is_deleted = false {query_filter}
            OFFSET {pagination["offset"]} LIMIT {pagination["limit"]};
        """
        return query
    
    def list_ranking_user_delayed_works_employess(self, pagination: dict):
        """
            report of the most delayed employees
            Filter Atrasado, No Atraso
        Args:
            pagination (dict): _description_
        """
        query_filter = ""
        if pagination["filter_by"]:
            query_filter = f"""AND (unaccent(username) ILIKE unaccent('%{pagination["filter_by"]}%'))"""
        
        query_order_by = ""
        if pagination["sort_by"] and pagination["order_by"]:
            query_order_by = f"""ORDER BY b.{pagination["order_by"]} {pagination["sort_by"]}"""
        
        query = f"""
            WITH employee_delays AS (
                SELECT
                    e.id AS employee_id,
                    u.id AS id_user,
                    INITCAP(TRIM(u.username)) AS username,
                    u.typecontract,
                    t.data,
                    t.entrada,
                    t.entrada_almoco,
                    t.saida_almoco,
                    t.entrada_lanche,
                    t.saida_lanche,
                    CASE 
                        WHEN t.entrada > t.data::date + '08:30:00'::time THEN 
                            EXTRACT(EPOCH FROM (t.entrada - (t.data::date + '08:30:00'::time))) / 60
                        ELSE 0
                    END AS atraso_entrada_minutos,
                    CASE 
                        WHEN t.saida_almoco > t.entrada_almoco + INTERVAL '1 hour' THEN 
                            EXTRACT(EPOCH FROM (t.saida_almoco - (t.entrada_almoco + INTERVAL '1 hour'))) / 60
                        ELSE 0
                    END AS atraso_saida_almoco_minutos,
                    CASE 
                        WHEN t.saida_lanche > t.entrada_lanche + INTERVAL '15 minutes' THEN 
                            EXTRACT(EPOCH FROM (t.saida_lanche - (t.entrada_lanche + INTERVAL '15 minutes'))) / 60
                        ELSE 0
                    END AS atraso_saida_lanche_minutos,
                    CASE
                        WHEN (t.entrada > t.data::date + '08:30:00'::time OR
                            t.saida_almoco > t.entrada_almoco + INTERVAL '1 hour' OR
                            t.saida_lanche > t.entrada_lanche + INTERVAL '15 minutes')
                        THEN 'Atrasado'
                        ELSE 'No Atraso'
                    END AS status_atraso

                FROM 
                    public.time_point t
                LEFT join employee e ON t.employee_id = e.id
                LEFT JOIN public.user u ON e.user_id = u.id
                where u.is_deleted = false and e.is_deleted = false
            )
            SELECT 
                id_user,
                username,
                typecontract,
                TO_CHAR(data, 'DD-MM-YYYY') AS data,
                TO_CHAR(entrada, 'HH24:MI:SS') AS entrada,
                TO_CHAR(entrada_almoco, 'HH24:MI:SS') as entrada_almoco,
                TO_CHAR(saida_almoco, 'HH24:MI:SS') as saida_almoco,
                TO_CHAR(entrada_lanche, 'HH24:MI:SS') as entrada_lanche,
                TO_CHAR(saida_lanche, 'HH24:MI:SS') as saida_lanche,
                atraso_entrada_minutos,
                atraso_saida_almoco_minutos,
                atraso_saida_lanche_minutos,
                status_atraso
            FROM 
                employee_delays t
            {"WHERE" if query_filter else ""}
            ORDER BY username, data;
        """
        return query
    