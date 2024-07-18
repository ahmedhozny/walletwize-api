from sqlalchemy import Column, Integer, String, CHAR, func, TIMESTAMP, text, Engine

from app.models.backup_models import BaseModel


class ChangeLog(BaseModel):
    __tablename__ = 'change_log'
    id = Column(Integer, primary_key=True, autoincrement=True)
    table_name = Column(String(50), nullable=False)
    row_id = Column(Integer, nullable=False)
    operation = Column(CHAR(1), nullable=False)
    change_time = Column(TIMESTAMP, server_default=func.now())
    sync_time = Column(TIMESTAMP, server_default=None)

    @staticmethod
    def create_triggers_for_table(engine, table_name):
        check_trigger_sql = """
        SELECT COUNT(*)
        FROM information_schema.TRIGGERS
        WHERE TRIGGER_SCHEMA = DATABASE() AND TRIGGER_NAME = :trigger_name;
        """

        trigger_definitions = [
            {
                "name": f"before_insert_{table_name}",
                "timing": "BEFORE INSERT",
                "body": f"""
                INSERT INTO change_log (table_name, row_id, operation)
                VALUES ('{table_name}', NEW.id, 'I');
                """
            },
            {
                "name": f"before_update_{table_name}",
                "timing": "BEFORE UPDATE",
                "body": f"""
                INSERT INTO change_log (table_name, row_id, operation)
                VALUES ('{table_name}', NEW.id, 'U');
                """
            },
            {
                "name": f"before_delete_{table_name}",
                "timing": "BEFORE DELETE",
                "body": f"""
                INSERT INTO change_log (table_name, row_id, operation)
                VALUES ('{table_name}', OLD.id, 'D');
                """
            },
        ]

        with engine.connect() as connection:
            for trigger in trigger_definitions:
                result = connection.execute(text(check_trigger_sql), {"trigger_name": trigger["name"]}).scalar()
                if result == 0:
                    create_trigger_sql = f"""
                    CREATE TRIGGER {trigger["name"]}
                    {trigger["timing"]} ON {table_name}
                    FOR EACH ROW
                    BEGIN
                        {trigger["body"]}
                    END;
                    """
                    connection.execute(text(create_trigger_sql))

    @staticmethod
    def create_triggers_for_sqlite_table(engine, table_name):
        check_trigger_sql = """
            SELECT name FROM sqlite_master
            WHERE type='trigger' AND name=:trigger_name;
            """

        trigger_definitions = [
            {
                "name": f"before_insert_{table_name}",
                "timing": "BEFORE INSERT",
                "body": f"""
                    INSERT INTO change_log (table_name, row_id, operation)
                    VALUES ('{table_name}', NEW.id, 'I');
                    """
            },
            {
                "name": f"before_update_{table_name}",
                "timing": "BEFORE UPDATE",
                "body": f"""
                    INSERT INTO change_log (table_name, row_id, operation)
                    VALUES ('{table_name}', NEW.id, 'U');
                    """
            },
            {
                "name": f"before_delete_{table_name}",
                "timing": "BEFORE DELETE",
                "body": f"""
                    INSERT INTO change_log (table_name, row_id, operation)
                    VALUES ('{table_name}', OLD.id, 'D');
                    """
            },
        ]

        with engine.connect() as connection:
            for trigger in trigger_definitions:
                result = connection.execute(text(check_trigger_sql), {"trigger_name": trigger["name"]}).fetchone()
                if not result:
                    create_trigger_sql = f"""
                        CREATE TRIGGER {trigger["name"]}
                        {trigger["timing"]} ON {table_name}
                        FOR EACH ROW
                        BEGIN
                            {trigger["body"]}
                        END;
                        """
                    connection.execute(text(create_trigger_sql))
