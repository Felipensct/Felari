from app import app, db

# Adicione esta linha abaixo do import
app.app_context().push()

# Agora você pode criar suas tabelas
db.create_all()
