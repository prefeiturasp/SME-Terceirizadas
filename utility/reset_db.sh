echo "Script para apagar bancos de dados, USAR APENAS EM DESENVOLVIMENTO"

echo "Isso irá apagar os bancos de dados, confirma? (S/N)"
read apagar

if [ "$apagar" != "${apagar#[Ss]}" ] ;then
    echo "Apagando bancos de dados..."
    export PGPASSWORD=adminadmin
    export PGOPTS="-h localhost -U admin "
    for dbname in $(psql $PGOPTS -d postgres -c "copy (select datname from pg_database where datname like 'terceirizadas%' or datname like 'test_terceirizadas%') to stdout") ; do
        echo "Apagando $dbname"
        dropdb $PGOPTS -i "$dbname"
    done
    createdb $PGOPTS terceirizadas
fi
