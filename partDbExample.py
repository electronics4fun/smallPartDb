import yaml
import json
import os

import yaegoResistors
import smallPartDb


def eng_to_float(x):
    if type(x) == float or type(x) == int:
        return x
    if 'k' in x:
        if x.endswith('k'):
            return float(x.replace('k', '')) * 1000
        if len(x) > 1:
            return float(x.replace('k', '.')) * 1000
        return 1000.0
    if 'M' in x:
        if x.endswith('M'):
            return float(x.replace('M', '')) * 1000000
        if len(x) > 1:
            return float(x.replace('M', '.')) * 1000000
        return 1000000.0
    return float(x)

if __name__ == '__main__':
    with open("settings.yaml") as stream:
        try:
            settings = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise RuntimeError(exc)
    partDb = smallPartDb.smallPartDb(settings['host'], settings['token'])

    # show info
    print(partDb)

    myE96Series = yaegoResistors.yaegoResistors("K", "0603", "F", "R", "", "07")
    ESeries = yaegoResistors.E96
    E96YaegoNumbers = myE96Series.generateYaegoNumbers(ESeries, yaegoResistors.MinMaxE96)
    E96Values = myE96Series.generateValues(ESeries, yaegoResistors.MinMaxE96)
    categoryName = "Resistors"
    kicad_footprint = "Resistor_SMD:R_0603_1608Metric"

    data = { 'name': "0603", 'comment': "", "eda_info": { 'kicad_footprint': kicad_footprint  } }
    postResp = partDb.writeFootprint(data)
    fpId = None
    if postResp.status_code == 422:
        partDb.getFootprints()
        fpId = partDb.lookupFootprint(data['name'])
    if postResp.status_code == 200:
        fpId = json.loads(postResp.text)["id"]

    data = { 'comment': "", 'name': "Yaego" }
    postResp = partDb.writeManufacturer(data)
    yaegoId = None
    if postResp.status_code == 422:
        partDb.getManufacturers()
        yaegoId = partDb.lookupManufacturer(data['name'])
    if postResp.status_code == 200:
        yaegoId = json.loads(postResp.text)["id"]

    manufacturer = {}
    manufacturer['id'] = "/api/manufacturers/" + str(yaegoId)
    manufacturing_status = "active"
    manufacturer_product_url = "https://www.yageo.com/en/Product/Index/rchip/lead_free"

    footprint = {}
    footprint['id'] = "/api/footprints/" + str(fpId)

    eda_info = {}
    eda_info['reference_prefix'] = "R"
    eda_info['visibility'] = True
    eda_info['exclude_from_bom'] = False
    eda_info['exclude_from_board'] = False
    eda_info['exclude_from_sim'] = False
    # Altium
    #eda_info['kicad_symbol'] = "R_IEEE"
    #eda_info['kicad_footprint'] = "RESC1608X55N, RESC1608X55L, RESC1608X55M"
    # Kicad
    eda_info['kicad_symbol'] = "Device:R"
    eda_info['kicad_footprint'] = kicad_footprint
        
    print("write resistors")
    partId = {}
    for x, in zip(E96YaegoNumbers):
        postResp = partDb.writePart(name=x, category=categoryName, comment="generated by " + os.path.basename(__file__))
        partId[x] = json.loads(postResp.text)["id"]

    partDb.getParts()

    print("patch resistors")
    for v, p in zip(E96Values, partDb.parts):
        eda_info['value'] = str(eng_to_float(v))

        part = {}

        part['manufacturer_product_number'] = p['name']
        part['manufacturer_product_url'] = manufacturer_product_url
        part['manufacturing_status'] = manufacturing_status
        #part['ipn'] = "123"
        strValue = eng_to_float(v)
        #strValue = ('%.15f' % strValue).rstrip('0').rstrip('.')
        part['description'] = "RES " + strValue + " OHM 1% 1/10W 0603"
        part['favorite'] = False
        part['eda_info'] = eda_info
        part['footprint'] = footprint
        part['manufacturer'] = manufacturer

        postResp = partDb.patchPart(p['id'], data=part)   

        attachments = {}
        attachments['url'] = "https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-RC_51_RoHS_P_5.pdf"
        attachments['name'] = "PYu-RC_51_RoHS_P_5.pdf"
        attachments['attachment_type'] = "/api/attachment_types/1"
        attachments['element'] = "/api/parts/" + str(p['id'])
        postResp = partDb.writeAttachment(name=attachments['name'], data=attachments)
        attachmentId = json.loads(postResp.text)["id"]

        # download attachment
        data = { "upload": { "downloadUrl": True }, "url": attachments['url'] }
        partDb.patchAttachment(attachmentId, data=data)


        parameters = [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}]
        parameters[0]['name'] = "Resistance"
        parameters[0]['value_typical'] = eng_to_float(v)
        parameters[0]['unit'] = "Ohm"

        parameters[1]['name'] = "Temperature Coefficient"
        parameters[1]['value_min'] = -200
        parameters[1]['value_max'] = 200
        parameters[1]['unit'] = "ppm/°C"

        parameters[2]['name'] = "Operating Temperature"
        parameters[2]['value_min'] = -55
        parameters[2]['value_max'] = 155
        parameters[2]['unit'] = "°C"

        parameters[3]['name'] = "Composition"
        parameters[3]['value_text'] = "Thick Film"

        parameters[4]['name'] = "Height - Seated (Max)"
        parameters[4]['value_typical'] = 0.55
        parameters[4]['unit'] = "mm"
        parameters[4]['value_text'] = "0.022\""

        parameters[5]['name'] = "Number of Terminations"
        parameters[5]['value_typical'] = 2

        parameters[6]['name'] = "Package / Case"
        parameters[6]['value_text'] = "0603 (1608 Metric)"

        parameters[7]['name'] = "Packaging"
        parameters[7]['value_text'] = "Tape & Reel (TR)"

        parameters[8]['name'] = "Power"
        parameters[8]['value_typical'] = 0.1
        parameters[8]['unit'] = "W"

        parameters[9]['name'] = "Ratings"
        parameters[9]['value_text'] = "7C1 RoHS w/out Exemption (100% Pb-Free)"

        parameters[10]['name'] = "Size / Dimension"
        parameters[10]['value_text'] = "0.063\" L x 0.031\" W (1.60mm x 0.80mm)"

        parameters[11]['name'] = "Base Product Number"
        parameters[11]['value_text'] = "RC0603"

        parameters[12]['name'] = "Supplier Device Package"
        parameters[12]['value_text'] = "0603"

        parameters[13]['name'] = "Tolerance"
        parameters[13]['value_min'] = -1
        parameters[13]['value_max'] = 1
        parameters[13]['unit'] = "%"

        for para in parameters:
            para['element'] = "/api/parts/" + str(p['id'])
            postResp = partDb.writeParameter(name=para['name'], data=para)
            # max and min values not written. Perhaps a bug...
            # patching is pointless here but stays until sure regarding bug.
            #print(str(i) + ", p: " + str(p) + ", r: " + str(postResp))
            if postResp.status_code == 201 or postResp.status_code == 200:
                parameterId = json.loads(postResp.text)["id"]
                partDb.patchParameter(parameterId, data=para)

        del(part)


    print("List all parts")
    status = partDb.getParts()
    if status.status_code == 200:
        for p in partDb.parts:
            print(str(p['id']) + ": " + p['name'])

    print("get all footprints")
    status = partDb.getFootprints()
    if status.status_code == 200:
        for c in partDb.footprints:
            print("id: " + str(c['id']) + ", name: " + c['name'])

    print("get all categories")
    status = partDb.getCategories()
    if status.status_code == 200:
        for c in partDb.categories:
            print("id: " + str(c['id']) + ", name: " + c['name'] + ", full_path: " + c['full_path'])

    print("get all manufacturers")
    status = partDb.getManufacturers()
    if status.status_code == 200:
        for m in partDb.manufacturers:
            print("id: " + str(m['id']) + ", name: " + m['name'] )

    print("get all attachments")
    status = partDb.getAttachments()
    if status.status_code == 200:
        for m in partDb.attachments:
            print("id: " + str(m['id']) + ", name: " + m['name'] )

    print("get all footprints")
    status = partDb.getFootprints()
    if status.status_code == 200:
        for f in partDb.footprints:
            print("id: " + str(f['id']) + ", name: " + f['name'] )
