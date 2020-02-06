PGPASSWORD=adminadmin
for dbname in $(psql -h localhost -U admin -d postgres -c "copy (select datname from pg_database where datname like 'terceirizadas%') to stdout") ; do
    echo "$dbname"
    #dropdb -i "$dbname"
done

