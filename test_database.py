from database import FormData
print([column.name for column in FormData.__table__.columns])

# valid_fields = {column.name for column in FormData.__table__.columns}  # Get actual DB fields
# form_data = {key: data[key] for key in data if key in valid_fields}  # Filter valid fields only
