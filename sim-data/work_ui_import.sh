#!/bin/sh
sleep 5
curl -X 'POST' \
  'http://pulser:8000/api/start-pulser' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@Pulser_Minimal_Data.xlsx;type=application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'