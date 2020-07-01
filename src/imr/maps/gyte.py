from .wfs import get_wfs


def gyte(layer_name, outfile=None, wms_codes=(10, )):
    wfs_server = 'https://maps.imr.no/geoserver/fisk/ows'
    wfs_ds = get_wfs(wfs_server)
    wfs_layer = wfs_ds.GetLayerByName(layer_name)

    from osgeo import ogr
    memdriver = ogr.GetDriverByName('MEMORY')
    ds = memdriver.CreateDataSource('gyte')
    layer = ds.CopyLayer(wfs_layer, layer_name)

    # Filter out features
    for fid in range(1, layer.GetFeatureCount() + 1):
        feature = layer.GetFeature(fid)
        wms_code = next(
            feature.GetField(i)
            for i in range(feature.GetFieldCount())
            if feature.GetFieldDefnRef(i).GetName() == 'wms_code'
        )
        if wms_code not in wms_codes:
            layer.DeleteFeature(fid)

    if outfile:
        jsondriver = ogr.GetDriverByName('GeoJSON')
        out = jsondriver.CreateDataSource(outfile)
        out.CopyLayer(layer, layer_name)
        del out

    return ds


def gyteomr_script():
    import sys
    args = sys.argv

    layers = {
        "blålange": "fisk:Blaalange_bw",
        "blåkveite": "fisk:Blaakveite_bw",
        "brisling": "fisk:Brisling_bw",
        "brosme": "fisk:Brosme_bw_3",
        "hvitting": "fisk:Hvitting_bw",
        "hyse": "fisk:hyse_nea_bw",
        "kolmule": "fisk:kolmule_bw_1_1",
        "kveite": "fisk:Kveite_bw",
        "kysttorsk_nord": "fisk:kysttorsk_n_62g_bw",
        "kysttorsk_sør": "fisk:Kysttorsk_soer_for_62N_bw",
        "lange": "fisk:Lange_bw",
        "lodde": "fisk:lodde_bw",
        "lysing": "fisk:Lysing_bw",
        "makrell": "fisk:makrell_bw",
        "makrellstørje": "fisk:Makrellstorje_bw",
        "nordsjøhyse": "fisk:Nordsjohyse_bw",
        "nordsjøsei": "fisk:NordsjoSei_bw",
        "nordsjøsild": "fisk:Nordsjosild_bw3",
        "nordsjøtorsk": "fisk:Nordsjotorsk_bw",
        "polartorsk": "fisk:Polartorsk_bw2",
        "rognkjeks": "fisk:rognkjeks_rognkall_bw",
        "rødspette": "fisk:Roedspette_bw",
        "taggmakrell": "fisk:Taggmakrell_bw",
        "tobis": "fisk:Tobis_gyteomrade",
        "torsk_nea": "fisk:torsk_nea_bw",
        "sei": "fisk:Sei_bw",
        "sei_nea": "fisk:sei_nea_bw",
        "sild_nvg": "fisk:nvgsild_bw",
        "snabeluer": "fisk:snabeluer_bw2",
        "vanliguer": "fisk:Vanliguer_bw",
        "øyepål": "fisk:Oyepaal_bw",
    }

    def print_valid_species():
        print("Valid species include: ")
        for k, v in layers.items():
            print(f'  - {k} ({v})')

    # Pop wms_code arg
    try:
        idx = [arg.startswith('--wms_codes=') for arg in args].index(True)
        wmscode_str = args.pop(idx)
    except ValueError:
        wmscode_str = '--wms_codes=10'
    codes = tuple([int(s) for s in wmscode_str.split("=")[1].split(",")])

    if len(args) != 3:
        print("GYTEOMR")
        print("   Download spawning area to geojson file\n")
        print("Usage:\n")
        print('gyteomr [--wms_codes=code1,code2,...] "species" out.geojson\n')
        print('By default, only wms code 10 ("gyteområde") is included.\n')
        print_valid_species()
        return

    species = args[1].lower()
    if species not in layers:
        layer = species
    else:
        layer = layers[species]

    try:
        gyte(layer_name=layer, outfile=args[2], wms_codes=codes)
    except ValueError:
        print(f"Unknown species: {args[1]}\n")
        print_valid_species()
