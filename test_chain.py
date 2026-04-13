import json
from AGENT4.AGENT4 import SourcingAgent
from AGENT5.AGENT5 import NegotiatorAgent
from AGENT6.AGENT6 import CostAnalystAgent
from AGENT7.AGENT7 import BusinessStrategistAgent

print("=== STARTING TEST ===")
state = {}

print("\n--- AGENT 4 ---")
a4 = SourcingAgent()
state = a4.search_suppliers(state)

print("\n--- AGENT 5 ---")
a5 = NegotiatorAgent()
state = a5.negotiate_prices(state)

print("\n--- AGENT 6 ---")
a6 = CostAnalystAgent()
state = a6.calculate_tco(state)

print("\n--- AGENT 7 ---")
a7 = BusinessStrategistAgent()
state = a7.generate_business_plan(state)

print("\n=== TEST COMPLETED SUCCESSFULLY ===")
