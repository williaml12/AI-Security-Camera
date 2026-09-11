// #include <Arduino_RouterBridge.h>

// #define PIR_PIN 8

// int get_pir_state()
// {
//     return digitalRead(PIR_PIN);
// }

// void setup()
// {
//     Serial.begin(115200);

//     pinMode(PIR_PIN, INPUT);

//     Bridge.begin();

//     Bridge.provide("get_pir_state", get_pir_state);

//     Serial.println("================================");
//     Serial.println("AI SECURITY CAMERA");
//     Serial.println("PIR TEST READY");
//     Serial.println("================================");
// }

// void loop()
// {
//     static int lastState = LOW;

//     int state = digitalRead(PIR_PIN);

//     if (state != lastState)
//     {
//         lastState = state;

//         if (state == HIGH)
//         {
//             Serial.println("PIR: MOTION DETECTED");
//         }
//         else
//         {
//             Serial.println("PIR: MOTION ENDED");
//         }
//     }

//     delay(50);
// }












#include <Arduino_RouterBridge.h>

#define PIR_PIN 8
#define LED_PIN 3

// PIR state variables
int pir_state = LOW;
int pir_state_prev = LOW;
unsigned long last_debounce_time = 0;
unsigned long debounce_delay = 50;  // 50ms debounce

// Function to get PIR state (for Python)
int get_pir_state()
{
    return digitalRead(PIR_PIN);
}

// Function to check motion and control LED with debounce
void check_motion()
{
    pir_state_prev = pir_state;
    pir_state = digitalRead(PIR_PIN);
    
    if (pir_state != pir_state_prev)
    {
        last_debounce_time = millis();
    }
    
    // Check if enough time has passed since last change
    if ((millis() - last_debounce_time) > debounce_delay)
    {
        if (pir_state == HIGH)
        {
            digitalWrite(LED_PIN, HIGH);
            Serial.println("PIR: MOTION DETECTED - LED ON");
        }
        else
        {
            digitalWrite(LED_PIN, LOW);
            Serial.println("PIR: MOTION ENDED - LED OFF");
        }
    }
}

void setup()
{
    Serial.begin(115200);
    
    pinMode(PIR_PIN, INPUT);
    pinMode(LED_PIN, OUTPUT);
    
    // Ensure LED starts OFF
    digitalWrite(LED_PIN, LOW);
    
    Bridge.begin();
    
    // Provide functions to RouterBridge
    Bridge.provide("get_pir_state", get_pir_state);
    Bridge.provide_safe("check_motion", check_motion);
    
    Serial.println("================================");
    Serial.println("AI SECURITY CAMERA");
    Serial.println("PIR + LED CONTROL READY");
    Serial.println("================================");
    Serial.println("PIR Pin: D8");
    Serial.println("LED Pin: D3");
    Serial.println("================================");
}

void loop()
{
    // Read PIR state
    pir_state_prev = pir_state;
    pir_state = digitalRead(PIR_PIN);
    
    // Control LED based on PIR state with debounce
    if (pir_state != pir_state_prev)
    {
        last_debounce_time = millis();
    }
    
    if ((millis() - last_debounce_time) > debounce_delay)
    {
        if (pir_state == HIGH)
        {
            digitalWrite(LED_PIN, HIGH);
            Serial.println("PIR: MOTION DETECTED");
        }
        else
        {
            digitalWrite(LED_PIN, LOW);
            Serial.println("PIR: MOTION ENDED");
        }
    }
    
    delay(50);
}