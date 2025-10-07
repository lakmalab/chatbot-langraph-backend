from typing import Dict


class PensionCalculator:

    def __init__(self):
        self.retirement_age = 60
        self.annual_interest_rate = 0.08
        self.pension_duration_years = 20

    def calculate_monthly_contribution(
            self,
            current_age: int,
            desired_monthly_pension: float
    ) -> Dict[str, float]:
        """
        Calculate required monthly contribution to achieve desired pension

        Formula uses Future Value of Annuity:
        FV = PMT × [(1 + r)^n - 1] / r

        Where:
        - FV = Future Value (corpus needed)
        - PMT = Monthly contribution (what we're solving for)
        - r = Monthly interest rate
        - n = Number of months until retirement
        """

        # Validate inputs
        if current_age < 18 or current_age >= 60:
            raise ValueError("Age must be between 18 and 59")

        if desired_monthly_pension <= 0:
            raise ValueError("Desired pension must be greater than 0")

        # Calculate time to retirement
        years_to_retirement = self.retirement_age - current_age
        months_to_retirement = years_to_retirement * 12

        # Monthly interest rate
        monthly_rate = self.annual_interest_rate / 12

        # Calculate total corpus needed at retirement
        # This is the lump sum needed to pay out the pension for 20 years
        total_corpus_needed = desired_monthly_pension * 12 * self.pension_duration_years

        # Adjust corpus for present value (accounting for interest during payout)
        # PV = FV / (1 + r)^n
        months_in_pension_period = self.pension_duration_years * 12
        present_value_factor = (1 + monthly_rate) ** months_in_pension_period
        adjusted_corpus = total_corpus_needed / present_value_factor

        # Calculate monthly contribution using FV of annuity formula
        # PMT = FV × r / [(1 + r)^n - 1]
        if months_to_retirement > 0:
            future_value_factor = ((1 + monthly_rate) ** months_to_retirement - 1) / monthly_rate
            monthly_contribution = adjusted_corpus / future_value_factor
        else:
            monthly_contribution = adjusted_corpus

        # Calculate total contribution
        total_contribution = monthly_contribution * months_to_retirement

        return {
            "monthly_contribution": round(monthly_contribution, 2),
            "total_months": months_to_retirement,
            "total_contribution": round(total_contribution, 2),
            "expected_pension": round(desired_monthly_pension, 2),
            "years_to_retirement": years_to_retirement,
            "interest_rate": self.annual_interest_rate
        }

    def calculate_expected_pension(
            self,
            current_age: int,
            monthly_contribution: float
    ) -> Dict[str, float]:
        """
        Calculate expected pension based on monthly contribution
        (Reverse calculation)
        """

        years_to_retirement = self.retirement_age - current_age
        months_to_retirement = years_to_retirement * 12
        monthly_rate = self.annual_interest_rate / 12

        # Calculate future value of contributions
        future_value = monthly_contribution * (((1 + monthly_rate) ** months_to_retirement - 1) / monthly_rate)

        # Calculate monthly pension from corpus
        months_in_pension_period = self.pension_duration_years * 12
        present_value_factor = (1 + monthly_rate) ** months_in_pension_period
        expected_monthly_pension = (future_value * present_value_factor) / (12 * self.pension_duration_years)

        return {
            "expected_monthly_pension": round(expected_monthly_pension, 2),
            "total_corpus": round(future_value, 2),
            "monthly_contribution": round(monthly_contribution, 2),
            "years_to_retirement": years_to_retirement
        }