from peewee import SqliteDatabase, Model, PrimaryKeyField, ForeignKeyField
from peewee import CharField, IntegerField, DateTimeField, FloatField, BooleanField, DateField


db = SqliteDatabase('./history.db')


class BaseModel(Model):
	id = PrimaryKeyField(unique=True)
	
	class Meta:
		database = db
		order_by = 'id'
	

class Command(BaseModel):
	user_id = IntegerField()
	command = CharField()
	city_id = IntegerField()
	city = CharField()
	command_time = DateTimeField()
	
	class Meta:
		bd_table = 'commands'


class CommandParam(BaseModel):
	date_in = DateField()
	date_out = DateField()
	hotel_night = IntegerField()
	count_hotel = IntegerField()
	photo = BooleanField()
	count_photo = IntegerField()
	price_min = FloatField()
	price_max = FloatField()
	hotel_distance_min = FloatField()
	hotel_distance_max = FloatField()
	command_id = ForeignKeyField(Command, related_name='param')
	
	class Meta:
		db_table = 'command_params'


class CommandResult(BaseModel):
	hotel_id = IntegerField()
	hotel_name = CharField()
	hotel_address = CharField()
	hotel_distance = FloatField()
	cost = FloatField()
	cost_night = FloatField()
	hotel_url = CharField()
	command_id = ForeignKeyField(Command, related_name='result')
	
	class Meta:
		db_table = 'command_results'


with db:
	db.create_tables([Command, CommandResult, CommandParam])
	