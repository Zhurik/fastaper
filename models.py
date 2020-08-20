"""
Модели для работы с БД
"""

from tortoise.models import Model
from tortoise import Tortoise, fields, run_async


class CargoRate(Model):
    """
    Модель данных для хранения в БД
    """

    date = fields.DateField(null=False)
    cargo_type = fields.CharField(null=False, max_length=255)
    rate = fields.FloatField(null=False)

    def __str__(self) -> str:
        return f"{self.date} - {self.cargo_type}"


async def run():
    """
    Пробуем подключиться к БД
    """

    await Tortoise.init(
        db_url="postgres://postgres:docker@db.localhost:5432/postgres",
        modules={
            "models": ["__main__"]
        }
    )

    await Tortoise.generate_schemas()


if __name__ == "__main__":
    run_async(run())
