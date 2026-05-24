def get_status(total_ton):

    if total_ton < 100:
        return "RENDAH"

    elif total_ton < 10000:
        return "SEDANG"

    return "TINGGI"


def get_recommendation(
    scope1,
    scope2,
    scope3
):

    highest = max(
        scope1,
        scope2,
        scope3
    )

    if highest == scope1:

        return """
        - Kurangi penggunaan bahan bakar fosil
        - Gunakan kendaraan efisien
        - Optimalkan proses pembakaran
        """

    elif highest == scope2:

        return """
        - Gunakan energi terbarukan
        - Optimalkan konsumsi listrik
        - Tingkatkan efisiensi energi
        """

    return """
    - Evaluasi supply chain
    - Optimalkan logistik
    - Kurangi emisi tidak langsung
    """