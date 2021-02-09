from flask import Flask, jsonify, request
from flaskext.mysql import MySQL
from fuzzywuzzy import fuzz

app = Flask(__name__)

# Database Configuration
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'poli1'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

app = Flask(__name__)


@app.route('/')
def hello_world():
    return "Horas dan selamatdgsffh datang!"


@app.route('/organ', methods=["GET"])
def organ():
    cur = mysql.connect().cursor()
    cur.execute('select * from diagnosis_penyakit_organ')
    list_organ = [dict((cur.description[i][0], value)
                       for i, value in enumerate(row)) for row in cur.fetchall()]
    return jsonify({'Daftar Organ': list_organ})


idOrgan = {}
@app.route('/organ/<int:id>', methods=["GET"])
def select_organ(id):
    cur = mysql.connect().cursor()
    cur.execute('select gejala, id, id_organ from diagnosis_penyakit_gejala where id_organ in (' + str(id) + ')')
    id = [dict((cur.description[i][0], value)
               for i, value in enumerate(row)) for row in cur.fetchall()]
    global idOrgan
    idOrgan = id
    return jsonify({'Gejala Pada Organ Terpilih': idOrgan})


gejala_user = {}
@app.route("/organ/gejala/", methods=["GET"])
def select_gejala():
    id = request.args.get('id')
    cur = mysql.connect().cursor()
    cur.execute('select gejala, id from diagnosis_penyakit_gejala where id in (' + str(id) + ')')
    all_gejala_inputed = [dict((cur.description[i][0], value)
                               for i, value in enumerate(row)) for row in cur.fetchall()]

    global gejala_user
    gejala_user = all_gejala_inputed
    return jsonify(gejala_user)


penyakit_set = {}
@app.route("/organ/gejala/matching", methods=["GET"])
def get_match():
    gejala = list(gejala_user)
    penyakit = []
    gejala_fix = []
    gejala_input = []
    gejala_db = []
    cur = mysql.connect().cursor()
    # cur.execute('select * from diagnosis_penyakit_gejala')
    cur.execute(
        'SELECT diagnosis_penyakit_penyakit.id, diagnosis_penyakit_penyakit.nama_penyakit, diagnosis_penyakit_penyakit.poliklinik, '
        'diagnosis_penyakit_gejala.gejala, '
        'diagnosis_penyakit_penyebab.penyebab, diagnosis_penyakit_pengobatan.pengobatan, diagnosis_penyakit_pencegahan.pencegahan '
        'FROM diagnosis_penyakit_penyakit '
        'INNER JOIN diagnosis_penyakit_gejala '
        'ON diagnosis_penyakit_penyakit.id = diagnosis_penyakit_gejala.penyakit_id '
        'INNER JOIN diagnosis_penyakit_penyebab '
        'ON diagnosis_penyakit_penyakit.id = diagnosis_penyakit_penyebab.penyakit_id '
        'INNER JOIN diagnosis_penyakit_pengobatan '
        'ON diagnosis_penyakit_penyakit.id = diagnosis_penyakit_pengobatan.penyakit_id '
        'INNER JOIN diagnosis_penyakit_pencegahan '
        'ON diagnosis_penyakit_penyakit.id = diagnosis_penyakit_pencegahan.penyakit_id')
    all_gejala_db = [dict((cur.description[i][0], value)
                        for i, value in enumerate(row)) for row in cur.fetchall()]

    if len(gejala) > 0:
        for i in range(0, len(gejala)):
            gejala_set = list(all_gejala_db)
            for j in range(0, len(gejala_set)):
                k = 0
                for a in gejala:
                    gejala_input.append(a['gejala'].lower().split(' '))
                for b in gejala_set:
                    gejala_db.append(b['gejala'].lower().split(' '))

                hasilMatching = ([
                    fuzz.partial_ratio(i, j)
                    for i in gejala_input
                    for j in gejala_db
                ])
                # return jsonify(hasilMatching)
                for y in range(0, len(hasilMatching)):
                    if hasilMatching[y] == 100:
                        gejala_fix.append([gejala_set[j], 1])
                    elif 90 <= hasilMatching[y] <= 99:
                        gejala_fix.append([gejala_set[j], 0.8])
                    elif 80 <= hasilMatching[y] <= 89:
                        gejala_fix.append([gejala_set[j], 0.7])
                    elif 70 <= hasilMatching[y] <= 79:
                        gejala_fix.append([gejala_set[j], 0.6])
                    elif 0 <= hasilMatching[y] <= 69:
                        gejala_fix.append([gejala_set[j], 0])

                for j in range(0, len(gejala_fix)):
                    gejala2 = gejala_fix[j][0]
                    poin = gejala_fix[j][1]
                    penyakit.append(["id Penyakit:",
                                     gejala2['id'],
                                     gejala2['nama_penyakit'],
                                     gejala2['penyebab'],
                                     "Rekomendasi:", gejala2['poliklinik'],
                                     "Nilai Matching:",poin])
                    global penyakit_set
                    penyakit_set = penyakit
                return jsonify(penyakit_set)
# def get_match():
#     gejala = []
#     gejala_db = []
#     gejala_db2 = []
#     penyakit = []
#     gejala_fix = []
#
#     for i in gejala_user:
#         gejala.append(i['gejala'].lower().split())
#
#     cur = mysql.connect().cursor()
#     # cur.execute('select * from diagnosis_penyakit_gejala')
#     cur.execute(
#         'select gejala, penyakit_id, diagnosis_penyakit_penyakit.nama_penyakit, diagnosis_penyakit_penyakit.poliklinik '
#         'from diagnosis_penyakit_gejala inner join diagnosis_penyakit_penyakit on diagnosis_penyakit_gejala.penyakit_id = diagnosis_penyakit_penyakit.id')
#     all_gejala_db = [dict((cur.description[i][0], value)
#                           for i, value in enumerate(row)) for row in cur.fetchall()]
#     for x in all_gejala_db:
#         gejala_db.append(x['gejala'].lower().split())
#
#     if len(gejala) > 0:
#         for i in range(0, len(gejala)):
#             gejala_set = all_gejala_db
#             for j in range(0, len(gejala_set)):
#                 hasilMatching = [
#                     fuzz.ratio(a, b)
#                     for a in gejala
#                     for b in gejala_db
#                 ]
#                 for y in range(0, len(hasilMatching)):
#                     if hasilMatching[y] == 100:
#                         gejala_fix.append([gejala_set[j], 1])
#                     elif 90 <= hasilMatching[y] <= 99:
#                         gejala_fix.append([gejala_set[j], 0.8])
#                     elif 80 <= hasilMatching[y] <= 89:
#                         gejala_fix.append([gejala_set[j], 0.7])
#                     elif 70 <= hasilMatching[y] <= 79:
#                         gejala_fix.append([gejala_set[j], 0.6])
#                     elif 0 <= hasilMatching[y] <= 69:
#                         gejala_fix.append([gejala_set[j], 0])
#                 # return jsonify(gejala_fix)
#
#             for j in range(0, len(gejala_fix)):
#                 gejala2 = gejala_fix[j][0]
#                 poin = gejala_fix[j][1]
#                 penyakit.append([gejala2['penyakit_id'], gejala2['poliklinik'], poin])
#                 global penyakit_set
#                 penyakit_set = penyakit
#             return jsonify(penyakit_set)
penyakit_point_fix = {}
@app.route("/organ/gejala/point", methods=["GET"])
def make_point():
    if len(penyakit_set) > 0:
        penyakit_gejala = []
        penyakit_sama = []
        point = 0
        list_point = []
        penyakit_poin = []
        fix_penyakit_point = []
        penyakit = 0
        for i in range(0, len(penyakit_set)):
            penyakit_sama.append(penyakit_set[i])

        for i in range(0, len(penyakit_set)):
            for j in range(0, len(penyakit_set)):
                if penyakit_sama[i][0] == penyakit_set[j][0]:
                    penyakit = penyakit_sama[i][1]
                    point += penyakit_set[j][7]
            penyakit_gejala.append(["id Penyakit:", penyakit,
                                    "Total Bobot:", point])
            point = 0

        for i in range(0, len(penyakit_gejala)):
            if penyakit_gejala[i] not in penyakit_poin:
                penyakit_poin.append(penyakit_gejala[i])
                list_point.append(penyakit_gejala[i][1])
        list_point = sorted(list_point, reverse=True)

        for i in range(0, len(list_point[:10])):
            for j in range(0, len(penyakit_poin)):
                if list_point[i] == penyakit_poin[j][1]:
                    if penyakit_poin[j] not in fix_penyakit_point:
                        fix_penyakit_point.append(penyakit_poin[j])
                        global penyakit_point_fix
                        penyakit_point_fix = fix_penyakit_point
        return jsonify(fix_penyakit_point[:10])
    return jsonify(penyakit_set)

@app.route("/organ/gejala/persen", methods=["GET"])
def make_percentage():
    rekomendasi_fix = []
    point_penyakit = penyakit_point_fix[0][3]
    cur = mysql.connect().cursor()
    cur.execute('SELECT COUNT(gejala) FROM diagnosis_penyakit_gejala')
    hasil_bagi = [dict((cur.description[i][0], value)
                        for i, value in enumerate(row)) for row in cur.fetchall()]

    rumus = (point_penyakit / hasil_bagi[0]["COUNT(gejala)"]) * 100

    rekomendasi_fix.append([penyakit_set[0][0], penyakit_set[0][1], penyakit_set[0][2], "Penyebab:", penyakit_set[0][3], penyakit_set[0][4],
                            penyakit_set[0][5], "Persentase (%):", rumus])

    return jsonify(rekomendasi_fix)

if __name__ == '__main__':
    app.run()
