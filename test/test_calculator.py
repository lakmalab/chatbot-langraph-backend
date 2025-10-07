from app.utils.pension_calculator import PensionCalculator

calc = PensionCalculator()

result = calc.calculate_monthly_contribution(
    current_age=30,
    desired_monthly_pension=50000
)

print("Pension Calculation Results:")
print(f"Current Age: 30")
print(f"Desired Pension: Rs. 50,000/month")
print(f"Required Monthly Contribution: Rs. {result['monthly_contribution']}")
print(f"Years to Retirement: {result['years_to_retirement']}")
print(f"Total Contribution: Rs. {result['total_contribution']}")