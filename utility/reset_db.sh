echo "Script para apagar bancos de dados, USAR APENAS EM DESENVOLVIMENTO"
BASEDIR=$(dirname "$0")
ENVFILE="$BASEDIR/../.env"
export PGPASSWORD=$(grep POSTGRES_PASSWORD $ENVFILE | cut -d '=' -f2)
POSTGRES_HOST=$(grep POSTGRES_HOST $ENVFILE | cut -d '=' -f2)
POSTGRES_PORT=$(grep POSTGRES_PORT $ENVFILE | cut -d '=' -f2)
POSTGRES_DB=$(grep POSTGRES_DB $ENVFILE | cut -d '=' -f2)
POSTGRES_USER=$(grep POSTGRES_USER $ENVFILE | cut -d '=' -f2)
PGOPTS="-h $POSTGRES_HOST -U $POSTGRES_USER -p $POSTGRES_PORT "

echo "Isso irá apagar os bancos de dados, confirma? (S/N)"
read apagar

if [ "$apagar" != "${apagar#[Ss]}" ] ;then
    echo "Apagando bancos de dados..."
    for dbname in $(psql $PGOPTS -d postgres -c "copy (select datname from pg_database where datname like '$POSTGRES_DB%' or datname like 'test_$POSTGRES_DB%') to stdout") ; do
        echo "Apagando $dbname"
        dropdb $PGOPTS -i "$dbname"
        if [ $? -ne 0 ] ;then
            echo "Houve um erro ao apagar o banco de dados. Abortando..."
            exit;
        fi
    done
    echo "Recriado banco de dados..."
    createdb $PGOPTS $POSTGRES_DB
fi
