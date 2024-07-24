# Instructions
## How to Use the System
### Setup and Installation

1. Install Python requirements:
   ```
   pip install -r requirements.txt
   ```

2. Navigate to the `src` folder and run `get.py`:
   ```
   cd src
   python get.py
   ```

### Running the Simulation

3. Open CupCarbon project:
   - Navigate to `src/cupcarbon/smartcitysimulation.cup`
   - Open the project in CupCarbon
   - Press "Run Simulation" in CupCarbon to start the simulation

   Note: Start the simulation after running `get.py`

### Activating Services

4. To activate all sensor services, run:
   ```
   python run_sensors.py
   ```

## Subscriptions

5. After starting the simulation, run `post.py`:
   ```
   python post.py
   ```

> **Note:** `OneM2M` should be running on `localhost` along with `MongoDB`.

> ps: You can use `docker compose up` to run the `OneM2M` along with `MongDB`. 