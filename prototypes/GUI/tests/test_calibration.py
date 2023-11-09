"""
Unit tests for the calibration module
"""
import numpy as np
from numpy.polynomial.polynomial import Polynomial

from modules.calibration import MatReading, Calibration
from modules.mat_handler import ROW_WIDTH, COL_HEIGHT, hex_string_to_array, mat_list_to_array


CONTRACT_MAX_ERROR_PERC = 15    # the maximum allowed percentage error as per our contract

# real mat readings stored as hex strings. 0lbs was unweighted, SHEET corresponds to the 6.213lbs aluminum sheet
MAT_READING_0LBS = "6f634353454d42363a3e48484a66695f51343a444334224640333e43524f36483e46372f3030373635484a483e282e34352a1b39352932373936262d262c281e2424292927343636301e222929211429261e2629282820242026231b24202425242f31322b1a1f21231b1224211b22251b1b17171316181115171819171c20211f14181b1d1b0f20231620222c2e22241e2223181d1e1f201f24272928191f22241f1427271c292c33362c2e272c2f212c2a2c2e2c34373d3b242c2e322a1b343026363913110f100e0f100b110e0f0f0f111414140c0e0e0f0c08100e0c1011131412131012130d1410111211121415150d1011120e0a12110f161718191615121519101415161716181b1d1f13181719150e1a181420220a090908070708050606070706070908080505060705040706050707121312100e10130d0e0f0f1110111214140e1010120e0b13100f1d1b1213130f0d0e120b0d0d0d0e0f0e1010100a0c0d0e0b080e0c0b0f11010000000000000000000000000000000000000000000000000000001b1e1c19161922171a1a1b1e1d1d1d2122171c1c1e17131f1b1a25282224221e1a1d291b1d1d1e2221202325261a1e1f211815211d1d262a1111100e0c0d140d0d0f0f1311101313140d1011120d0b110f0f1315191c1a17131622171617171a1a191a1d1e1418181b14121b17171e2302000000000000000000000000000200000000000000000000000000030303030203040203030303030203040403030404030304030505071f23211d181c2f1e1d1f1f2224212125291b2122251a1b251f222a340808070605060c0706060607080709080806060607050507060607090f11100f0b0e170e0e1111121211121416101215160e13151117181f0808080706070a060708080908090a0a0b080a0a0c070a0b090d0d121d201e1b171a39271f1e1e222b1f2023271b1f20231815221c1d22261111100e0c0e1d120f0f101217101212140d0f11130c0b120f1012140807070605060e0806060607090708070806060607050407060607080809080806070f09070808080a0809090a0708090a0606090809090a060606050405080505060606070607070806070909060608060a080a0c0e120c090b150a0a1513110d0e12111810120e110d081810100e101012180f0c0e1a0d0d1c1917101216161d15161116110a201615111606050604040407040409080705060807090707050705030f0808060714171e130e1220111125201d15181d1e291c1d171c170e2c1d1b171c0a0b0d0806080e07080f0e0d0a0b0e0e120d0e0b0d0b061a100e0b0d191d241914172715162e28251b1e23253124261e261f11432c2720271a1e271814172a15152f29251b1e23242f23251c241d103524231d241113160f0d0e190d0e1e1a18111319192217181218130b221617131701000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000f131a0f0c0e1a0e0d201b18101215161c16181117110a1d14151216191e2a1813162c1614312a251a1b1f2129222319221b0f2a1e1f1a200606090504040804040a09080505080708070706070603090607060810131a0f0c0e170c0d201b18101215161b17191117140b1d1517121602010101010001000101010100000201010101000101000101010000151b25171214231213342c27181a1d2128242619231b0f281e201a1f11141c110d0f1a0d0d29211d111216171c1a1a1218120a1c1416121612151b110e0f1a0e0f27211e1314181a1f1e20141d170c1f1719141a0c0e120c0a0b120a0a1d19160e0e11121616160e1510081610130f130c0d120c090a1109091e19150c0d10101414130c120e07140f100d100f10150e0b0c150b0c25211c10111315191a1a1118120918111511150e10140d0b0c140a0b211d190f101214181a190f1710091711120f1315181e1411121d10123b332c17191c1e2225241822180d22191c181e1012160f0c0f170c0d25231e111216171a201e121c120a1a1416121715171d1310121d1010302a2515171b1d2226231722180d221a1c171f181b2017121521121438342c191b1f22272c291b291c0f271e211b24111318100d0e180c0d2a251f111216181b1d1b121a120a1b14161217"
MAT_READING_SHEET = "c8a7928a858186837d8982868a8989878a86868a85827f857e819184b9b4b0ceaeadbab5adceb6bccececebfcebfbecebcb6b2b7adb0b5b3605a55595452555652595455595958585958575857565457535457545c58565a58555959565b57595b5b5b5a5b5a5a5b5a5b5b6059595c5a504d4b4e4b494d4c4a4e4b4c4e4d4f4e4e4e4f4f4e4e4d524d4e514f5f5e5b5d5b595d5c5e5d595b5d5d5d5d5d5d5d5d5c5c5a5f5b5b5f5e575553555452565558555354555556565656575655555255525256565b59575a58575b595b5a57595a5a5a5b5b5d5d5b5a5a575a58575b5c565452565453575657565355565656575658595656565457545458593d3b3a3d3b3b3f3f3e3e3b3c3d3c3e3e3e40423e3e3c3b3d3a3b3e3f4a4a4a4b4a4a4e4e4e4c4a4c4c4a4b4b4b4c4c4b4a49474b47474a4b494a4a48484849474849464848484948494949484746444844464a4a4b4b4b4c4a4b4c4a494c494b4c4c4c4c4c4d4d4c4b4a484b47484c4d171615151516151413151515141517141416151515151415141516164b4d4d4c4a4d4d4a4a4d494c4c4c4c4d4d4d4d4d4b4a484c474a4d4e606061625e61625e5c635e616262626262646363615e5c625b5e606348474748454b48454548464848484948484948484745434742444647302e2f2f2d33302e2c2f2d2e2f2f2f2f2f2f302f2f2e2d302d3031363f3e3f3f3c403f3c3d413d404040403f404240403f3e3d413c3f3f42424041423e4343403e413f41424242414245434241413e423e4041435a59595c565a5c575459565a5b5b5b5a5b5d5c5b5c5c585e575c5e643836363935363a37383a383b3a3a3a393a3b393a393736383536373844424147404146444046434647474746474b484747474347424444464947474a45464c48454a47494a4a4a494a4c4b4a4b4a474b46484a4c514f4f554c4e56524e5451535454565253585555555351544d505253535051554e4f56534e5452545555555455595855555451544f505253403e3e433c3d44423d434242434343424346444344413f413c3e3f405552525850505b585158575658585857585c5c585d575457525354546663626c61616b67626c6d696c6c6c6a6c71716c7a6b686b656666685a57555f5555615e575e5b5d5f5f605d5f615f5f655e5a5f575859585e5c5862585863605a615d606262626162616162625f5d645a5c5c5c625f5c675c5c67645e6761656767686667686866696362675f6060614e4c49514948514f4b514d4f515151505151545154504e514c4c4c4c5655535d53525b58545b565a5c5c5b5c5d5d5d5c5b5857595455565654524f574f4f5b5953585556575757585857575858575556525352536563626a6161706a616b67696a6b6a6d6b69696b6b6c6c69666665667572707b7170887d727b76787b7b7b7e7b7a7c7b7f7f7b7a747574756562606b6161716a616b65686b6b6b6f6b696a6b69686868646665665a58565f57576960585f595c5f5e5e605f5f615f605f625e595a595a504e4d554d4e58534d5551535555565655545555545356534e4f4f503e3c3c3f3e3e45423c403e3f3f404040403f3f403f3e3f3e3b3c3c3d3634343835353a3935383838383838383837383837373838343535355b59575f57585e5d585f5d5f5f5f5f5f5f5e5f5f5e5d615f595a5a5b3836353a36373939373a3b3e3b3a3a3a3a39393a38383737343536365857555e55555b59555e595c5e5e5e615d5d5f5e5e5f5e605a5a585b06050505050504040505050404050605040405050404040404040404423f3f463f3e42413f46414546444546454645464444424440424040312f2d312d2d302f2d312f3131313131313232313130303230312f312d2b2a2e2b2a2d2c2b2e2e2e2e2e2e2e2e2f302e2f2e2e302f2f2d2f211f1f211f1f212120222325222222212220222222212022212221213a38373c39383c3b393c40443c3d3c3c3d3d3d3d3b39383a3739393b605d5c655f5d63635f66717e656565646566676564615f625d6061643f3c3b413d3c3f3e3c4143454141414141434541413e3d3f3c3e3e4143413f454241434340454648454545444446494546424144404445474845444b48464a49444a4b4d4a4a4a4a4a4b4d4a4c4846494549494a2b28272a2a292a2a272b2a2b29292b292a2b2b2a2a29282a282b2c2c"


def test_two_samples_ideal():
    """
    Test which covers fitting a curve to two flawless samples of the mat
    """
    # create a calibrator
    cal = Calibration(ROW_WIDTH, COL_HEIGHT, polyfit_degree=1)

    # add two samples 
    array = np.zeros((ROW_WIDTH, COL_HEIGHT))
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, 1, array)
    cal.add_reading(reading)

    array = np.ones((ROW_WIDTH, COL_HEIGHT))
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, 1, array)
    cal.add_reading(reading)

    # calculate the curves
    cal.calculate_calibration_curves()

    # expect the result to be y = 1. Test
    x = np.arange(ROW_WIDTH * COL_HEIGHT, dtype=np.uint8).reshape((ROW_WIDTH, COL_HEIGHT))
    y = cal.apply_calibration_curve(x)

    truth = np.ones((ROW_WIDTH, COL_HEIGHT), dtype=np.double)

    assert np.array_equal(y, truth)


def test_five_samples_ideal():
    """
    Test which covers fitting a curve to five flawless samples of the mat
    """
    # create a calibrator
    cal = Calibration(ROW_WIDTH, COL_HEIGHT, polyfit_degree=4)

    # add 5 samples, fitting y = 0.001(x^2) + 0.001x + 1
    poly = Polynomial([1, 0.001, 0.001])
    array = np.full((ROW_WIDTH, COL_HEIGHT), 0, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, poly(0), array)
    cal.add_reading(reading)

    array = np.full((ROW_WIDTH, COL_HEIGHT), 32, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, poly(32), array)
    cal.add_reading(reading)

    array = np.full((ROW_WIDTH, COL_HEIGHT), 64, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, poly(64), array)
    cal.add_reading(reading)

    array = np.full((ROW_WIDTH, COL_HEIGHT), 128, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, poly(128), array)
    cal.add_reading(reading)

    array = np.full((ROW_WIDTH, COL_HEIGHT), 255, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, poly(255), array)
    cal.add_reading(reading)

    # calculate the curves
    cal.calculate_calibration_curves()

    # expect the result to be y = 1. Test
    x = np.arange(ROW_WIDTH * COL_HEIGHT, dtype=np.uint8).reshape((ROW_WIDTH, COL_HEIGHT))
    y = cal.apply_calibration_curve(x)

    # generate the expected result
    truth = np.arange(ROW_WIDTH * COL_HEIGHT, dtype=np.double)
    for i in range(len(truth)):
        truth[i] = poly(int(truth[i]) % 256)

    truth = np.round(truth.reshape((ROW_WIDTH, COL_HEIGHT)), 2)

    # compare the actual and expected results. Interestingly enough, they are not exact
    perc_errors = np.empty((ROW_WIDTH, COL_HEIGHT))
    for i in range(ROW_WIDTH):
        for j in range(COL_HEIGHT):
            perc_errors[i, j] = 100 * ((y[i, j] - truth[i, j]) / truth[i, j])    # 100 * (meas - true) / true

    perc_error = np.max(np.abs(perc_errors.flatten()))
    print(f"Maximum percentage error between the true value and the polyfit value: {perc_error}")

    assert perc_error < CONTRACT_MAX_ERROR_PERC


def test_ten_samples_ideal_bad_case():
    """
    Test which covers fitting a curve to ten flawless samples of the mat
    Expects awful error due to the high degree the polynomial is fit to
    """
    # create a calibrator
    cal = Calibration(ROW_WIDTH, COL_HEIGHT, polyfit_degree=9)

    # add 5 samples, fitting y = 0.001(x^2) + 0.001x + 1
    poly = Polynomial([1, 0.001, 0.001])
    array = np.full((ROW_WIDTH, COL_HEIGHT), 0, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, poly(0), array)
    cal.add_reading(reading)

    array = np.full((ROW_WIDTH, COL_HEIGHT), 8, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, poly(8), array)
    cal.add_reading(reading)

    array = np.full((ROW_WIDTH, COL_HEIGHT), 16, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, poly(16), array)
    cal.add_reading(reading)

    array = np.full((ROW_WIDTH, COL_HEIGHT), 32, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, poly(32), array)
    cal.add_reading(reading)

    array = np.full((ROW_WIDTH, COL_HEIGHT), 48, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, poly(48), array)
    cal.add_reading(reading)

    array = np.full((ROW_WIDTH, COL_HEIGHT), 64, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, poly(64), array)
    cal.add_reading(reading)

    array = np.full((ROW_WIDTH, COL_HEIGHT), 96, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, poly(96), array)
    cal.add_reading(reading)

    array = np.full((ROW_WIDTH, COL_HEIGHT), 128, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, poly(128), array)
    cal.add_reading(reading)

    array = np.full((ROW_WIDTH, COL_HEIGHT), 192, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, poly(192), array)
    cal.add_reading(reading)

    array = np.full((ROW_WIDTH, COL_HEIGHT), 255, dtype=np.uint8)
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, poly(255), array)
    cal.add_reading(reading)

    # calculate the curves
    cal.calculate_calibration_curves()

    # expect the result to be y = 1. Test
    x = np.arange(ROW_WIDTH * COL_HEIGHT, dtype=np.uint8).reshape((ROW_WIDTH, COL_HEIGHT))
    y = cal.apply_calibration_curve(x)

    # generate the expected result
    truth = np.arange(ROW_WIDTH * COL_HEIGHT, dtype=np.double)
    for i in range(len(truth)):
        truth[i] = poly(int(truth[i]) % 256)

    truth = np.round(truth.reshape((ROW_WIDTH, COL_HEIGHT)), 2)

    # compare the actual and expected results. Interestingly enough, they are not exact
    perc_errors = np.empty((ROW_WIDTH, COL_HEIGHT))
    for i in range(ROW_WIDTH):
        for j in range(COL_HEIGHT):
            perc_errors[i, j] = 100 * ((y[i, j] - truth[i, j]) / truth[i, j])    # 100 * (meas - true) / true

    perc_error = np.max(np.abs(perc_errors.flatten()))
    print(f"Maximum percentage error between the true value and the polyfit value: {perc_error}")

    # Surprisingly, using a higher order polynomial seems to not have much affect until order 8 - 9, where error begins to explode
    # expect 2652.48 percent error (bad)
    assert perc_error > CONTRACT_MAX_ERROR_PERC


def test_two_samples_real_measurements():
    
    # create a calibrator
    cal = Calibration(ROW_WIDTH, COL_HEIGHT, polyfit_degree=1)

    array = mat_list_to_array(hex_string_to_array(MAT_READING_0LBS))
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, 0, array)
    cal.add_reading(reading)

    array = mat_list_to_array(hex_string_to_array(MAT_READING_SHEET))
    reading = MatReading(ROW_WIDTH, COL_HEIGHT, 6.213, array)
    cal.add_reading(reading)

    # calculate the curves
    cal.calculate_calibration_curves()

    # expect the result to be y = 1. Test
    x = np.full(ROW_WIDTH * COL_HEIGHT, 255, dtype=np.uint8).reshape((ROW_WIDTH, COL_HEIGHT))
    y = cal.apply_calibration_curve(x)

    print(x)
    print(y)