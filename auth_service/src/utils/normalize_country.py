import pycountry


def normalize_country(value: str) -> str:
    value = value.strip()

    country = pycountry.countries.get(name=value)

    if not country:
        country = pycountry.countries.get(alpha_2=value.upper())

    if not country:
        country = pycountry.countries.get(alpha_3=value.upper())

    if not country:
        for c in pycountry.countries:
            if c.name.lower() == value.lower():
                country = c
                break

    if not country:
        raise ValueError(f"Unknown country: {value}")

    return country.name
