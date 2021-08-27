
export MIMIR_PATH="./mimir"
export TEMP_DIR=$(mktemp -d)
export TEMP_FILE="${TEMP_DIR}/out.proto"
wget -O "${TEMP_FILE}" https://raw.githubusercontent.com/FRRouting/frr/master/grpc/frr-northbound.proto 
python -m grpc_tools.protoc  --python_out="${MIMIR_PATH}/providers/frr/client" --grpc_python_out="${MIMIR_PATH}/providers/frr/client" -I ${TEMP_DIR} out.proto
rm -r ${TEMP_DIR}