from utils_mtmc.get_mtmc_files import *
import numpy as np


def run_distance_by_plane_in_switzerland_in_2015():
    df_zp = get_zp_renamed()
    # select only people who were asked questions about trips with overnights (module 1b, encoded 2)
    df_zp = df_zp[df_zp['module_attributed_to_the_respondent'] == 2]
    # select only people who said the number of trips with overnights they made
    df_zp_with_trips = df_zp[df_zp['nb_trips_with_overnights'] > 0]
    df_zp_without_trips = df_zp[df_zp['nb_trips_with_overnights'] == 0]
    del df_zp
    # sum of weights of the declared trips, including those without details, in particular distance
    weight_declared_trips = df_zp_with_trips['WP'].sum()
    # select overnight trips whose distance is known
    df_overnight_trips = get_overnight_trips_in_2015_renamed()  # contains all trips with overnights
    df_overnight_trips = df_overnight_trips[df_overnight_trips['trip_distance'] >= 0]  # only trips with valid distance
    df_overnight_trips = add_aggregate_goal_to_overnight_trips(df_overnight_trips)  # add info about aggregated goals
    # get number of detailed trips (with distance) by person
    df_overnight_trips_count_nb = df_overnight_trips[['HHNR', 'trip_distance']].groupby('HHNR').count()
    df_overnight_trips_count_nb = df_overnight_trips_count_nb.rename(columns={'trip_distance': 'nb_detailed_trips'})
    df_zp_with_trips = pd.merge(df_zp_with_trips, df_overnight_trips_count_nb,
                                left_on='HHNR', right_index=True, how='left')
    # get total distance per person by plane
    df_overnight_trips['trip_distance_by_plane'] = \
        df_overnight_trips['trip_distance'] * (df_overnight_trips['main_transport_mode'] == 17)
    df_overnight_trips['trip_distance_by_plane_private'] = \
        df_overnight_trips['trip_distance'] * (df_overnight_trips['main_transport_mode'] == 17) \
        * (df_overnight_trips['trip_goal_agg'] == 1)
    df_overnight_trips['trip_distance_by_plane_business'] = \
        df_overnight_trips['trip_distance'] * (df_overnight_trips['main_transport_mode'] == 17) \
        * (df_overnight_trips['trip_goal_agg'] == 2)
    df_overnight_trips['trip_distance_by_plane_other'] = \
        df_overnight_trips['trip_distance'] * (df_overnight_trips['main_transport_mode'] == 17) \
        * (df_overnight_trips['trip_goal_agg'] == 3)
    df_overnight_trips_count_sum = df_overnight_trips[['HHNR', 'trip_distance_by_plane',
                                                       'trip_distance_by_plane_private',
                                                       'trip_distance_by_plane_business',
                                                       'trip_distance_by_plane_other']].groupby('HHNR').sum()
    df_overnight_trips_count_sum = \
        df_overnight_trips_count_sum.rename(columns={'trip_distance_by_plane': 'total_distance',
                                                     'trip_distance_by_plane_private': 'total_distance_private',
                                                     'trip_distance_by_plane_business': 'total_distance_business',
                                                     'trip_distance_by_plane_other': 'total_distance_other'})
    df_zp_with_trips = pd.merge(df_zp_with_trips, df_overnight_trips_count_sum,
                                left_on='HHNR', right_index=True, how='inner')
    # extrapolation for all trips based on declared trips
    df_zp_with_trips['total_distance_extrapolated'] = \
        df_zp_with_trips['total_distance'] * df_zp_with_trips['nb_trips_with_overnights'] / \
        df_zp_with_trips['nb_detailed_trips']
    df_zp_with_trips['total_distance_extrapolated_private'] = \
        df_zp_with_trips['total_distance_private'] * df_zp_with_trips['nb_trips_with_overnights'] / \
        df_zp_with_trips['nb_detailed_trips']
    df_zp_with_trips['total_distance_extrapolated_business'] = \
        df_zp_with_trips['total_distance_business'] * df_zp_with_trips['nb_trips_with_overnights'] / \
        df_zp_with_trips['nb_detailed_trips']
    df_zp_with_trips['total_distance_extrapolated_other'] = \
        df_zp_with_trips['total_distance_other'] * df_zp_with_trips['nb_trips_with_overnights'] / \
        df_zp_with_trips['nb_detailed_trips']
    # Remove people who said they did a trip, but whose distance are not valid
    # For HHNR=333950, the distance is known, but not the country of destination.
    # For HHNR=488907, the destination is known but is the same as home.
    df_zp_with_trips = df_zp_with_trips[~df_zp_with_trips['HHNR'].isin([333950, 488907])]
    print('Basis total distance:', len(df_zp_with_trips) + len(df_zp_without_trips),
          'persons who were asked about trips with overnights and with a valid information about the distance')
    # Result: 17054
    # Sum of weights of the detailed trips, without those missing details, in particular distance
    weight_detailed_trips = df_zp_with_trips['WP'].sum()
    # Correction factor for people declaring they did trips, but without detailing them
    correction_factor_declared_detailed_trips = weight_declared_trips / weight_detailed_trips
    # Trips have been asked for 3 months and must be extrapolated for a year
    extrapolation_factor_3_months_to_1_year = 365.0 / 120
    print('Total distance of trips by plane per person and per year, in km:',
          (df_zp_with_trips['WP'] * df_zp_with_trips['total_distance_extrapolated']).sum() *
          correction_factor_declared_detailed_trips /
          (df_zp_with_trips['WP'].sum() * correction_factor_declared_detailed_trips + df_zp_without_trips['WP'].sum())
          * extrapolation_factor_3_months_to_1_year)
    # Result: 5924.873511771452
    print('Only private trips:',
          (df_zp_with_trips['WP'] * df_zp_with_trips['total_distance_extrapolated_private']).sum() *
          correction_factor_declared_detailed_trips /
          (df_zp_with_trips['WP'].sum() * correction_factor_declared_detailed_trips + df_zp_without_trips['WP'].sum())
          * extrapolation_factor_3_months_to_1_year)
    print('Only business trips:',
          (df_zp_with_trips['WP'] * df_zp_with_trips['total_distance_extrapolated_business']).sum() *
          correction_factor_declared_detailed_trips /
          (df_zp_with_trips['WP'].sum() * correction_factor_declared_detailed_trips + df_zp_without_trips['WP'].sum())
          * extrapolation_factor_3_months_to_1_year)
    print('Only other trips:',
          (df_zp_with_trips['WP'] * df_zp_with_trips['total_distance_extrapolated_other']).sum() *
          correction_factor_declared_detailed_trips /
          (df_zp_with_trips['WP'].sum() * correction_factor_declared_detailed_trips + df_zp_without_trips['WP'].sum())
          * extrapolation_factor_3_months_to_1_year)


def get_zp_renamed():
    selected_columns = ['HHNR', 'WP', 'dmod', 'f70100']
    df_zp = get_zp(year=2015, selected_columns=selected_columns)
    # Rename variables
    df_zp = df_zp.rename(columns={'dmod': 'module_attributed_to_the_respondent',
                                  'f70100': 'nb_trips_with_overnights'})
    return df_zp


def get_overnight_trips_in_2015_renamed():
    selected_columns = ['HHNR', 'WP', 'RENR', 'reisenr', 'f70801', 'f71300', 'f71400_01', 'f71600b',
                        'f70700_01', 'f71700b']
    df_overnight_trips = get_overnight_trips(year=2015, selected_columns=selected_columns)
    # Rename variables
    df_overnight_trips = df_overnight_trips.rename(columns={'f71600b': 'trip_distance',
                                                            'f71700b': 'trip_distance_in_CH',
                                                            'f70700_01': 'trip_goal',
                                                            'f70801': 'main_transport_mode'})
    return df_overnight_trips


def add_aggregate_goal_to_overnight_trips(df_overnight_trips):
    conditions_trip_goal = [df_overnight_trips['trip_goal'].isin([2,  # private: shopping
                                                                  3,  # Private: medical
                                                                  5,  # private: visit friends and family
                                                                  6,  # Private: gastronomie
                                                                  7,  # Private: active sport
                                                                  8,  # Private: hiking
                                                                  9,  # Private: bike tour
                                                                  10,  # Private: passive sport
                                                                  11,  # Private: outdoor activities (no sport)
                                                                  12,  # Private: Culture and leisure
                                                                  13,  # Private: Holidays, trips
                                                                  14,  # Private: Religion
                                                                  16,  # Private: Accompany for private trips
                                                                  17,  # Private: Round trip
                                                                  ]),
                            df_overnight_trips['trip_goal'].isin([4,  # Work: business trip
                                                                  15,  # Work: Accompany for work trips
                                                                  ])]
    choices_trip_goal = [1, 2]  # private (1), business (2), other (3, as default)
    df_overnight_trips['trip_goal_agg'] = np.select(conditions_trip_goal, choices_trip_goal, default=3)
    return df_overnight_trips


if __name__ == '__main__':
    run_distance_by_plane_in_switzerland_in_2015()
