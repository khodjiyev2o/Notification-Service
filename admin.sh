
# curl -X 'POST' -H "Content-Type: application/json" -d @users.json http://localhost:8000/users/create_admin_by_script/


curl -X 'POST' \
  'http://13.114.193.241/users/create_admin_by_script/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d @users.json