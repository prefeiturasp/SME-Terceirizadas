export PGPASSWORD=adminadmin
export PGOPTS="-h localhost -U admin "
for dbname in $(psql $PGOPTS -d postgres -c "copy (select datname from pg_database where datname like 'terceirizadas%' or datname like 'test_terceirizadas%') to stdout") ; do
    echo "Apagando $dbname"
    dropdb $PGOPTS -i "$dbname"
done
createdb $PGOPTS terceirizadas
