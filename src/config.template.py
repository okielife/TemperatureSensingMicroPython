# ---- WiFi ----
WIFI_NETWORKS = [
    ("Primary Wi-Fi Network Name", "Primary Wi-Fi Network Password"),  # preferred, deployed location
    ("Secondary Wi-Fi Network Name", "Secondary Wi-Fi Network Password"),  # backup, home, during development
]

# ---- Timing ----
GITHUB_PUSH_INTERVAL_MS = 3_600_000

# ---- Connected sensor labels and roms with names from the list below ----
CONNECTED_SENSORS = [
    ("03", "2893645b000000b4", "Emerald_Garage_Frig"),
    ("13", "28a70f46d438683a", "Emerald_Garage_Frzr")
]
KNOWN_SENSOR_DATA = [
    "Must match the config in https://github.com/okielife/TempSensors/blob/main/_data/config.json",
    "** really should keep these to 21 characters or less..."
    "123456789012345678901",
    "Emerald_Garage_Frig",
    "Emerald_Garage_Frzr",
    "Emerald_Kitchen_Frzr",
    "Emerald_Kitchen_Frig",
    "P_Garage_Freezer",
    "P_South_Vert_Freezer",
    "P_South_Vert_Fridge",
    "P_South_Deep_Freeze",
    "P_Dining_Deep_Freeze",
    "P_Dining_East_Freeze",  # currently missing
    "P_Dining_West_Freeze",
    "P_Entry_West_Fridge",
    "P_Entry_West_Freezer",
    "P_Entry_East_Fridge",
    "P_Entry_East_Freezer",
    "P_West_Vert_Freezer",
]
KNOWN_SENSOR_ROMS = {
    # try to keep up to date with the canon data at https://github.com/okielife/TempSensors/blob/main/_data/sensor_roms.json
    "01": "2887bb81e3813ccd",
    "02": "286ea75e00000061",
    "03": "2893645b000000b4",
    "04": "28890946d40d332a",
    "05": "28b22346d41723ec",
    "06": "282e6246d45e2ed0",
    "07": "28280a46d4db00a1",
    "08": "28f15346d41d7b53",
    "09": "28249b46d44b1d05",
    "10": "28ad5846d4587455",
    "11": "283fd646d49c3115",
    "12": "28767446d4f06336",
    "13": "28a70f46d438683a",
    "14": "28031280e3e13cee",
    "15": "282aae80e3e13ca0",
    "16": "282d670e000000b7",
    "17": "28821d0e0000001f",
    "18": "286c045704c53c29",
}

# ---- GitHub token with push access to the dashboard repo ----
GITHUB_TOKEN = "ghp_abc123def456abc123def456abc123def456"
