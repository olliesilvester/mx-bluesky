from store_in_ispyb import StoreInIspyb


class StoreInIspyb3D(StoreInIspyb):
    def __init__(self, ispyb_config):
        super().__init__(ispyb_config)

    def _store_scan_data(self):
        data_collection_group_id = self._store_data_collection_group_table()
        position_id = self._store_position_table()

        data_collection_id_1 = self._store_data_collection_table(
            position_id, data_collection_group_id
        )

        grid_id_1 = self._store_grid_info_table(data_collection_id_1)

        self.__prepare_second_scan_params()

        data_collection_id_2 = self._store_data_collection_table()

        grid_id_2 = self._store_grid_info_table(data_collection_id_2)

        return [data_collection_id_1, data_collection_id_2], [grid_id_1, grid_id_2]

    def __prepare_second_scan_params(self):
        self.omega_start -= 90
        self.run_number += 1
