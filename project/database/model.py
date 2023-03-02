from peewee import SqliteDatabase, Model, PrimaryKeyField, ForeignKeyField
from peewee import CharField, IntegerField, DateTimeField, FloatField


db = SqliteDatabase('history.db')


class BaseModel(Model):
	id = PrimaryKeyField(unique=True)
	
	class Meta:
		database = db
		order_by = 'id'
	

class Command(BaseModel):
	user_id = IntegerField()
	command = CharField()
	params = CharField(null=True)
	command_time = DateTimeField()
	
	class Meta:
		bd_table = 'commands'


class ResultCommand(BaseModel):
	hotel_id = IntegerField()
	hotel_name = CharField()
	hotel_address = CharField()
	hotel_distance = FloatField()
	hotel_price = FloatField()
	hotel_url = CharField()
	command_id = ForeignKeyField(Command)
	
	class Meta:
		db_table = 'resultscommands'


with db:
	db.create_tables([Command, ResultCommand])
	