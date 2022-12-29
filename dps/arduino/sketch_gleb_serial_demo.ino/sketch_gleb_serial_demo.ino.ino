// motor params
const int in1 = 8, in2 = 0, in3 = 10, in4 = 11;

// the code below has been adapted from https://forum.arduino.cc/t/demo-of-pc-arduino-comms-using-python/219184/5
// arduino - pc communication params
const int BAUDRATE = 9600;
const byte buffSize = 40;
char inputBuffer[buffSize];
const char startMarker = '<';
const char endMarker = '>';
byte bytesRecvd = 0;
boolean readInProgress = false;
boolean gotCommandFromPC = false;
char cmd_motor_id[buffSize] = {0};
int cmd_motor_write_sleep = 0;
int cmd_num_motor_moves = 0;

void setup()
{
    pinMode(in1, OUTPUT);
    pinMode(in2, OUTPUT);
    pinMode(in3, OUTPUT);
    pinMode(in4, OUTPUT);
    Serial.begin(BAUDRATE);
    Serial.println("<Arduino is ready>");
}

void loop()
{
  getDataFromPC();
  if (gotCommandFromPC) {
    executeCommandFromPC();
  }
  replyToPC();
}

void getDataFromPC() {
  // receive data from PC and save it into inputBuffer
  if(Serial.available() > 0) {
    char x = Serial.read();
    // the order of these IF clauses is significant
    if (x == endMarker) {
      readInProgress = false;
      gotCommandFromPC = true;
      inputBuffer[bytesRecvd] = 0;
      parseDataIntoCommand();
    }
    
    if(readInProgress) {
      inputBuffer[bytesRecvd] = x;
      bytesRecvd ++;
      if (bytesRecvd == buffSize) {
        bytesRecvd = buffSize - 1;
      }
    }

    if (x == startMarker) { 
      bytesRecvd = 0; 
      readInProgress = true;
    }
  }
}

void parseDataIntoCommand() {
  // split the data into its parts  
  char * strtokIndx; // this is used by strtok() as an index
  
  strtokIndx = strtok(inputBuffer, ",");      // get the first part - the string
  strcpy(cmd_motor_id, strtokIndx); // copy it to cmd_motor_id
  
  strtokIndx = strtok(NULL, ","); // this continues where the previous call left off
  cmd_motor_write_sleep = atoi(strtokIndx);     // convert this part to an integer
  
  strtokIndx = strtok(NULL, ","); 
  cmd_num_motor_moves = atoi(strtokIndx);     // convert this part to a float
}

void replyToPC() {
  if (gotCommandFromPC) {
    gotCommandFromPC = false;
    Serial.println("<>");
  }
}

// read a command from serial and do proper action
void executeCommandFromPC() {
  if (strcmp(cmd_motor_id, "MOTOR_ID") != 0) {
    return;
  }
    int i = 0;
    while (i < cmd_num_motor_moves) {
    digitalWrite(in1, HIGH); 
    digitalWrite(in2, LOW); 
    digitalWrite(in3, LOW); 
    digitalWrite(in4, HIGH);
    delay(cmd_motor_write_sleep);

    digitalWrite(in1, HIGH); 
    digitalWrite(in2, HIGH); 
    digitalWrite(in3, LOW); 
    digitalWrite(in4, LOW);
    delay(cmd_motor_write_sleep);

    digitalWrite(in1, LOW); 
    digitalWrite(in2, HIGH); 
    digitalWrite(in3, HIGH); 
    digitalWrite(in4, LOW);
    delay(cmd_motor_write_sleep);

    digitalWrite(in1, LOW); 
    digitalWrite(in2, LOW); 
    digitalWrite(in3, HIGH); 
    digitalWrite(in4, HIGH);
    delay(cmd_motor_write_sleep);
    i = i + 1;
    }
}