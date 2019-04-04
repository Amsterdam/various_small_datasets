function publish_table {
	# $1 is target table base name, so milieuzones
	# The variablesmileuzones_new and mileuzones_old are derived

	TABLE_TARGET=$1
	 TABLE_NEW=${1}_new
	TABLE_OLD=${1}_old

	psql -X --set ON_ERROR_STOP=on <<SQL
BEGIN;
ALTER TABLE IF EXISTS $TABLE_TARGET RENAME TO $TABLE_OLD;
ALTER TABLE $TABLE_NEW RENAME TO $TABLE_TARGET;
DROP TABLE IF EXISTS $TABLE_OLD;
COMMIT;
SQL

}
