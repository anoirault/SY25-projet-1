#include <array>
#include <WiFiNINA.h>
#include <string.h>

#include "arduino_secrets.h"

#define AP_SWITCH_TIME  20000
#define SCAN_INTERVAL   5000


int status;
int nb_networks = 0;
int current_ap_idx = 0;

uint32_t start_time;
uint32_t last_switch_time = 0;
uint32_t last_scan_time;

void setup () {
    Serial.begin(9600);
    while (!Serial) {;}

    // check for the WiFi module:
    if (WiFi.status() == WL_NO_MODULE) {
        while (true);
    }

    nb_networks = WiFi.scanNetworks();
    
    start_time = millis();
    last_scan_time = start_time;
}



bool is_ssid_visible(const char *ssid) {
    // which AP are we looking for
    for (int i=0; i<nb_networks; i++) {
        const char *curr_ssid = WiFi.SSID(i);
        // Serial.println(curr_ssid);

        if (strcmp(curr_ssid, ssid) == 0) {
            return true;
        }
    }
    return false;
}


bool try_connect_ap_idx(int ap_idx) {
    status = WiFi.status();

    const char *ssid = APS[ap_idx].ssid;
    const char *pass = APS[ap_idx].pass;

    for (int retries = 0; retries < 5; retries++) {
        status = WiFi.begin(ssid, pass);

        if (status == WL_CONNECTED) return true;
    }

    return false;
}

void loop () {
    uint32_t now = millis();

    status = WiFi.status();


    // scan surrounding networks and output to serial at set interval
    if(now - last_scan_time > SCAN_INTERVAL) {
        nb_networks = WiFi.scanNetworks();

        for(int i=0; i<nb_networks; i++) {
            print_ap_info(i);
        }
        last_scan_time = now;
    }

    // switch to the next known and visible AP at set interval
    // if (now - last_switch_time > AP_SWITCH_TIME) {
    //     WiFi.end();
    //     for(int i=0; i<NB_APS; i++) {
    //         current_ap_idx = (current_ap_idx + 1) % NB_APS;
    //         const char *search_ssid = APS[current_ap_idx].ssid;

    //         if(is_ssid_visible(search_ssid)) {
    //             break;
    //         }
    //     }
    //     last_switch_time = now;
    // }

    // // reconnect to currently selected network if necessary
    // status = WiFi.status();
    // if (status != WL_CONNECTED) {
    //     Serial.print("// connecting to: ");
    //     Serial.println(APS[current_ap_idx].ssid);
    //     try_connect_ap_idx(current_ap_idx);
    // } else {
    //     // only print current AP info if connected
    //     print_connected_ap_info();
    // }


    // delay(100);
}

void print_mac(uint8_t mac[6]) {
    for (int j=0; j<6; j++) {
        // pad values less than 16
        if(mac[j] < 0x10) Serial.print(0);

        Serial.print(mac[j], 16);

        // don't print spacer after last number
        if (j < 5) Serial.print(":");
    }
}

void print_ap_info(int idx) {
    Serial.print(WiFi.SSID(idx));
    Serial.print("|");
    
    uint8_t mac[6];
    WiFi.BSSID(idx, mac);

    print_mac(mac);

    Serial.print("|");
    Serial.print(WiFi.RSSI(idx));
    Serial.println();
}

void print_connected_ap_info() {
    Serial.print(WiFi.SSID());
    Serial.print("|");
    
    uint8_t mac[6];
    WiFi.BSSID(mac);

    print_mac(mac);

    Serial.print("|");
    Serial.print(WiFi.RSSI());
    Serial.println();
}