
export MIMIR_PATH="./mimir"
export TEMP_DIR=$(mktemp -d)
export FILENAME="frr-northbound.proto"
export TEMP_FILE="${TEMP_DIR}/${FILENAME}"
wget -O "${TEMP_FILE}" https://raw.githubusercontent.com/FRRouting/frr/master/grpc/${FILENAME}
python -m grpc_tools.protoc  --python_out="${MIMIR_PATH}/frr/client" --grpc_python_out="${MIMIR_PATH}/frr/client" -I ${TEMP_DIR} ${FILENAME}
rm -r ${TEMP_DIR}