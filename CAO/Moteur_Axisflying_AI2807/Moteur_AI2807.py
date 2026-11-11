# BASTARD - Moteur Axisflying AI2807 1300KV, modele detaille (sans les fils)
# Script Fusion 360 : parametres utilisateur, esquisses cotees et corps
# (embase, stator, bobinages, aimants, cloche a 8 rayons, arbre M5).
# Repere : Z = axe de rotation, Z = 0 = face d'appui de l'embase,
#          pattes de fixation sur les axes X et Y.

import adsk.core
import adsk.fusion
import math
import traceback

# nom, expression, commentaire
PARAMETRES = [
    # --- mesures au pied a coulisse ---
    ('MOT_diam_cloche',        '33.62 mm', 'Diametre exterieur de la cloche - MESURE'),
    ('MOT_hauteur_corps',      '20.52 mm', 'Dessous embase -> dessus cloche - MESURE'),
    ('MOT_hauteur_totale',     '35.68 mm', 'Dessous embase -> bout de l arbre - MESURE'),
    ('MOT_ext_pattes',         '25.05 mm', 'Bout a bout de deux pattes opposees - MESURE'),
    ('MOT_diam_moyeu_embase',  '14.44 mm', 'Moyeu central de l embase - MESURE (interpretation)'),
    # --- donnees fabricant ---
    ('MOT_entraxe_trous',      '19 mm',    'Diametre du cercle des 4 trous M3 - FABRICANT'),
    ('MOT_diam_trou',          '3 mm',     'Trous de fixation M3 - FABRICANT'),
    ('MOT_diam_arbre',         '5 mm',     'Arbre M5 - FABRICANT'),
    ('MOT_diam_stator',        '28 mm',    'Diametre du stator (2807) - FABRICANT'),
    ('MOT_h_stator',           '7 mm',     'Hauteur du stator (2807) - FABRICANT'),
    # --- estimations d apres les photos ---
    ('MOT_ep_embase',          '2.5 mm',   'Epaisseur de l embase - ESTIME'),
    ('MOT_jeu_cloche',         '1 mm',     'Jeu entre embase et bas de cloche - ESTIME'),
    ('MOT_ep_paroi',           '1.2 mm',   'Epaisseur de la paroi de cloche - ESTIME'),
    ('MOT_ep_aimant',          '1.2 mm',   'Epaisseur des aimants - ESTIME'),
    ('MOT_h_aimant',           '9 mm',     'Hauteur des aimants - ESTIME'),
    ('MOT_ep_flasque',         '2.2 mm',   'Epaisseur du flasque a rayons - ESTIME'),
    ('MOT_saillie_moyeu',      '1 mm',     'Depassement du moyeu au-dessus du flasque - ESTIME'),
    ('MOT_diam_moyeu_cloche',  '11 mm',    'Moyeu central de la cloche - ESTIME'),
    ('MOT_chanfrein_cloche',   '1.5 mm',   'Chanfrein du haut de la cloche - ESTIME'),
    ('MOT_rayon_raccord',      '1.2 mm',   'Raccords entre pattes et moyeu - ESTIME'),
    ('MOT_long_lisse',         '5.5 mm',   'Partie lisse de l arbre - ESTIME'),
    ('MOT_diam_roulement',     '9 mm',     'Logement du roulement sous l embase - ESTIME'),
    ('MOT_z_stator',           '6.5 mm',   'Hauteur du bas du stator - ESTIME'),
    # --- valeurs calculees ---
    ('MOT_z_cloche',   'MOT_ep_embase + MOT_jeu_cloche',                          'Bas de la cloche - CALCULE'),
    ('MOT_z_flasque',  'MOT_hauteur_corps - MOT_saillie_moyeu - MOT_ep_flasque',  'Dessous du flasque - CALCULE'),
    ('MOT_long_arbre', 'MOT_hauteur_totale - MOT_hauteur_corps',                  'Arbre au-dessus de la cloche - CALCULE'),
]

# Valeurs numeriques (mm) utilisees pour tracer ; les cotes sont ensuite liees aux parametres
D_CLOCHE, EXT_PATTES, D_MOYEU_EMB, ENTRAXE, D_TROU = 33.62, 25.05, 14.44, 19.0, 3.0
D_ARBRE, D_STATOR, EP_PAROI, EP_AIMANT, D_MOYEU_CL, D_ROUL = 5.0, 28.0, 1.2, 1.2, 11.0, 9.0
LARG_RAYON = 2.6
NB_RAYONS, NB_DENTS, NB_AIMANTS = 8, 12, 14


def run(context):
    ui = None
    avert = []
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox('Ouvre d\'abord un document de conception (espace Conception).')
            return
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        VI = adsk.core.ValueInput
        P3 = adsk.core.Point3D
        OP = adsk.fusion.FeatureOperations
        ORI = adsk.fusion.DimensionOrientations

        # ---------- 1. Parametres utilisateur ----------
        up = design.userParameters
        for nom, expr, com in PARAMETRES:
            p = up.itemByName(nom)
            if p:
                p.expression = expr
            else:
                up.add(nom, VI.createByString(expr), 'mm', com)

        # ---------- 2. Composant ----------
        root = design.rootComponent
        try:
            occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
            comp = occ.component
        except:
            comp = root   # document "Part Design" : un seul composant autorise
        try:
            comp.name = 'Moteur_Axisflying_AI2807'
        except:
            pass

        # ---------- Outils ----------
        def tenter(nom, fonction):
            """Execute un detail ; en cas d'echec le note sans arreter le script."""
            try:
                return fonction()
            except:
                avert.append(nom)
                return None

        def esquisse(nom):
            sk = comp.sketches.add(comp.xYConstructionPlane)
            sk.name = nom
            return sk

        def cercle(sk, diam_mm, expr, centre=None):
            """Cercle (centre sur l'origine par defaut) dont le diametre est lie a une expression."""
            c = sk.sketchCurves.sketchCircles.addByCenterRadius(
                centre if centre else sk.originPoint, diam_mm / 20.0)
            try:
                g = c.centerSketchPoint.geometry
                d = sk.sketchDimensions.addDiameterDimension(
                    c, P3.create(g.x + diam_mm / 28.0, g.y + diam_mm / 28.0, 0))
                d.parameter.expression = expr
            except:
                avert.append('cote ' + expr)
            return c

        def ligne_polaire(sk, r1, a1, r2, a2):
            """Segment fixe entre deux points donnes en (rayon mm, angle deg)."""
            l = sk.sketchCurves.sketchLines.addByTwoPoints(
                P3.create(r1 / 10.0 * math.cos(math.radians(a1)), r1 / 10.0 * math.sin(math.radians(a1)), 0),
                P3.create(r2 / 10.0 * math.cos(math.radians(a2)), r2 / 10.0 * math.sin(math.radians(a2)), 0))
            l.isFixed = True
            return l

        def ligne_decalee(sk, axe_deg, decal, r_deb, r_fin):
            """Segment parallele a l'axe radial axe_deg, decale lateralement de decal (mm)."""
            a = math.radians(axe_deg)
            ux, uy, vx, vy = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
            l = sk.sketchCurves.sketchLines.addByTwoPoints(
                P3.create((r_deb * ux + decal * vx) / 10.0, (r_deb * uy + decal * vy) / 10.0, 0),
                P3.create((r_fin * ux + decal * vx) / 10.0, (r_fin * uy + decal * vy) / 10.0, 0))
            l.isFixed = True
            return l

        def polaire(profil):
            """Centre de gravite du profil : (rayon mm, angle deg)."""
            c = profil.areaProperties(adsk.fusion.CalculationAccuracy.LowCalculationAccuracy).centroid
            return math.hypot(c.x, c.y) * 10.0, math.degrees(math.atan2(c.y, c.x))

        def ecart(angle, pas):
            """Ecart angulaire au multiple de 'pas' le plus proche."""
            return abs(((angle + pas / 2.0) % pas) - pas / 2.0)

        def profils(sk):
            return [sk.profiles.item(i) for i in range(sk.profiles.count)]

        def anneau(sk):
            """Dans une esquisse a deux cercles concentriques : le profil annulaire."""
            ps = profils(sk)
            for p in ps:
                if p.profileLoops.count >= 2:
                    return p
            return max(ps, key=lambda p: p.areaProperties(
                adsk.fusion.CalculationAccuracy.LowCalculationAccuracy).area)

        def extruder(liste, z0, h, op, nom, cible=None):
            col = adsk.core.ObjectCollection.create()
            for p in liste:
                col.add(p)
            exts = comp.features.extrudeFeatures
            inp = exts.createInput(col, op)
            inp.setDistanceExtent(False, VI.createByString(h))
            inp.startExtent = adsk.fusion.OffsetStartDefinition.create(VI.createByString(z0))
            if cible:
                inp.participantBodies = [cible]
            f = exts.add(inp)
            f.name = nom
            return f

        def nommer(f, nom):
            n = f.bodies.count
            for i in range(n):
                f.bodies.item(i).name = nom if n == 1 else '{}_{:02d}'.format(nom, i + 1)

        # =====================================================================
        # 3. EMBASE : moyeu + 4 pattes, trous M3, logement de roulement, palier
        # =====================================================================
        sk = esquisse('Esq_embase')
        cercle(sk, D_MOYEU_EMB, 'MOT_diam_moyeu_embase')
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]

        def centre_patte(s, dx, dy):
            """Point place sur un axe, a MOT_entraxe_trous / 2 de l'origine."""
            pt = s.sketchPoints.add(P3.create(dx * ENTRAXE / 20.0, dy * ENTRAXE / 20.0, 0))
            try:
                if dx != 0:
                    s.geometricConstraints.addHorizontalPoints(s.originPoint, pt)
                    d = s.sketchDimensions.addDistanceDimension(
                        s.originPoint, pt, ORI.HorizontalDimensionOrientation,
                        P3.create(dx * ENTRAXE / 40.0, -0.25, 0))
                else:
                    s.geometricConstraints.addVerticalPoints(s.originPoint, pt)
                    d = s.sketchDimensions.addDistanceDimension(
                        s.originPoint, pt, ORI.VerticalDimensionOrientation,
                        P3.create(-0.25, dy * ENTRAXE / 40.0, 0))
                d.parameter.expression = 'MOT_entraxe_trous / 2'
            except:
                avert.append('cote entraxe')
            return pt

        for dx, dy in directions:
            cercle(sk, EXT_PATTES - ENTRAXE, 'MOT_ext_pattes - MOT_entraxe_trous', centre_patte(sk, dx, dy))
        f = extruder(profils(sk), '0 mm', 'MOT_ep_embase', OP.NewBodyFeatureOperation, 'Embase')
        embase = f.bodies.item(0)
        embase.name = 'Embase'

        def raccords_embase():
            col = adsk.core.ObjectCollection.create()
            for e in embase.edges:
                if e.geometry.curveType == adsk.core.Curve3DTypes.Line3DCurveType:
                    col.add(e)
            if col.count == 0:
                raise Exception('aucune arete')
            ff = comp.features.filletFeatures
            fi = ff.createInput()
            try:
                fi.edgeSetInputs.addConstantRadiusEdgeSet(col, VI.createByString('MOT_rayon_raccord'), False)
            except:
                fi.addConstantRadiusEdgeSet(col, VI.createByString('MOT_rayon_raccord'), False)
            ff.add(fi).name = 'Raccords_embase'
        tenter('raccords de l\'embase', raccords_embase)

        sk = esquisse('Esq_trous_M3')
        for dx, dy in directions:
            cercle(sk, D_TROU, 'MOT_diam_trou', centre_patte(sk, dx, dy))
        extruder(profils(sk), '0 mm', 'MOT_ep_embase', OP.CutFeatureOperation, 'Trous_M3', embase)

        def roulement():
            s = esquisse('Esq_roulement')
            cercle(s, D_ROUL, 'MOT_diam_roulement')
            extruder(profils(s), '0 mm', '0.8 mm', OP.CutFeatureOperation, 'Logement_roulement', embase)
            s2 = esquisse('Esq_vis_arbre')
            cercle(s2, 4.0, '4 mm')
            nommer(extruder(profils(s2), '0.2 mm', '0.6 mm', OP.NewBodyFeatureOperation, 'Vis_arbre'), 'Vis_arbre')
        tenter('logement du roulement', roulement)

        def palier():
            s = esquisse('Esq_palier')
            cercle(s, 10.0, '10 mm')
            extruder(profils(s), 'MOT_ep_embase', 'MOT_z_stator + MOT_h_stator - MOT_ep_embase',
                     OP.JoinFeatureOperation, 'Palier', embase)
        tenter('palier central', palier)

        # =====================================================================
        # 4. STATOR : culasse + 12 dents
        # =====================================================================
        def stator():
            s = esquisse('Esq_culasse_stator')
            cercle(s, 15.0, '15 mm')
            cercle(s, 10.0, '10 mm')
            f = extruder([anneau(s)], 'MOT_z_stator', 'MOT_h_stator', OP.NewBodyFeatureOperation, 'Culasse_stator')
            corps = f.bodies.item(0)
            corps.name = 'Stator'

            s = esquisse('Esq_dents_stator')
            cercle(s, 14.8, '14.8 mm')
            cercle(s, D_STATOR - 2.0, 'MOT_diam_stator - 2 mm')
            cercle(s, D_STATOR, 'MOT_diam_stator')
            pas = 360.0 / NB_DENTS
            rs = D_STATOR / 2.0
            for k in range(NB_DENTS):
                a = k * pas
                ligne_decalee(s, a, 1.3, 7.1, rs - 0.7)
                ligne_decalee(s, a, -1.3, 7.1, rs - 0.7)
                ligne_polaire(s, rs - 1.3, a - 12.0, rs + 0.3, a - 12.0)
                ligne_polaire(s, rs - 1.3, a + 12.0, rs + 0.3, a + 12.0)
            choisis = []
            for p in profils(s):
                r, ang = polaire(p)
                if r > 8.0 and ecart(ang, pas) < 4.0:
                    choisis.append(p)
            if len(choisis) != 2 * NB_DENTS:
                avert.append('dents du stator ({} profils sur {})'.format(len(choisis), 2 * NB_DENTS))
            extruder(choisis, 'MOT_z_stator', 'MOT_h_stator', OP.JoinFeatureOperation, 'Dents_stator', corps)
        tenter('stator', stator)

        # =====================================================================
        # 5. BOBINAGES : 12 bobines autour des dents
        # =====================================================================
        def bobinages():
            s = esquisse('Esq_bobinages')
            cercle(s, 16.0, '16 mm')
            cercle(s, D_STATOR - 2.6, 'MOT_diam_stator - 2.6 mm')
            pas = 360.0 / NB_DENTS
            for k in range(NB_DENTS):
                for da in (-12.5, 12.5):
                    ligne_polaire(s, 7.6, k * pas + da, D_STATOR / 2.0 - 1.0, k * pas + da)
            choisis = []
            for p in profils(s):
                r, ang = polaire(p)
                if r > 8.0 and ecart(ang, pas) < 4.0:
                    choisis.append(p)
            f = extruder(choisis, 'MOT_z_stator - 1.5 mm', 'MOT_h_stator + 3 mm',
                         OP.NewBodyFeatureOperation, 'Bobinages')
            nommer(f, 'Bobine')
        tenter('bobinages', bobinages)

        # =====================================================================
        # 6. AIMANTS : 14 aimants colles dans la cloche
        # =====================================================================
        def aimants():
            s = esquisse('Esq_aimants')
            r_ext = D_CLOCHE / 2.0 - EP_PAROI
            r_int = r_ext - EP_AIMANT
            cercle(s, 2 * r_ext, 'MOT_diam_cloche - 2 * MOT_ep_paroi')
            cercle(s, 2 * r_int, 'MOT_diam_cloche - 2 * MOT_ep_paroi - 2 * MOT_ep_aimant')
            pas = 360.0 / NB_AIMANTS
            for k in range(NB_AIMANTS):
                for da in (-(pas / 2.0 - 1.2), pas / 2.0 - 1.2):
                    ligne_polaire(s, r_int - 0.3, k * pas + da, r_ext + 0.3, k * pas + da)
            choisis = []
            for p in profils(s):
                r, ang = polaire(p)
                if r > 10.0 and ecart(ang, pas) < 5.0:
                    choisis.append(p)
            f = extruder(choisis, 'MOT_z_stator - 1 mm', 'MOT_h_aimant',
                         OP.NewBodyFeatureOperation, 'Aimants')
            nommer(f, 'Aimant')
        tenter('aimants', aimants)

        # =====================================================================
        # 7. CLOCHE : paroi, flasque chanfreine, 8 fenetres, moyeu
        # =====================================================================
        sk = esquisse('Esq_paroi_cloche')
        cercle(sk, D_CLOCHE, 'MOT_diam_cloche')
        cercle(sk, D_CLOCHE - 2 * EP_PAROI, 'MOT_diam_cloche - 2 * MOT_ep_paroi')
        f = extruder([anneau(sk)], 'MOT_z_cloche', 'MOT_z_flasque - MOT_z_cloche',
                     OP.NewBodyFeatureOperation, 'Paroi_cloche')
        cloche = f.bodies.item(0)
        cloche.name = 'Cloche'

        sk = esquisse('Esq_flasque_cloche')
        cercle(sk, D_CLOCHE, 'MOT_diam_cloche')
        extruder(profils(sk), 'MOT_z_flasque', 'MOT_ep_flasque', OP.JoinFeatureOperation, 'Flasque_cloche', cloche)

        def chanfrein_cloche():
            z_haut = max(e.boundingBox.maxPoint.z for e in cloche.edges)
            col = adsk.core.ObjectCollection.create()
            for e in cloche.edges:
                bb = e.boundingBox
                if abs(bb.minPoint.z - z_haut) < 1e-5 and abs(bb.maxPoint.z - z_haut) < 1e-5:
                    if abs((bb.maxPoint.x - bb.minPoint.x) - D_CLOCHE / 10.0) < 1e-3:
                        col.add(e)
            if col.count == 0:
                raise Exception('aucune arete')
            cf = comp.features.chamferFeatures
            try:
                ci = cf.createInput2()
                ci.chamferEdgeSets.addEqualDistanceChamferEdgeSet(
                    col, VI.createByString('MOT_chanfrein_cloche'), False)
            except:
                ci = cf.createInput(col, False)
                ci.setToEqualDistance(VI.createByString('MOT_chanfrein_cloche'))
            cf.add(ci).name = 'Chanfrein_cloche'
        tenter('chanfrein de la cloche', chanfrein_cloche)

        def fenetres():
            s = esquisse('Esq_fenetres_cloche')
            r1 = D_MOYEU_CL / 2.0 + 0.5
            r2 = D_CLOCHE / 2.0 - EP_PAROI - 0.6
            cercle(s, 2 * r1, 'MOT_diam_moyeu_cloche + 1 mm')
            cercle(s, 2 * r2, 'MOT_diam_cloche - 2 * MOT_ep_paroi - 1.2 mm')
            pas = 360.0 / NB_RAYONS
            for k in range(NB_RAYONS):
                for d in (-LARG_RAYON / 2.0, LARG_RAYON / 2.0):
                    ligne_decalee(s, k * pas, d, r1 - 1.2, r2 + 0.6)
            choisis = []
            for p in profils(s):
                r, ang = polaire(p)
                if r > 8.0 and ecart(ang, pas) > 10.0:
                    choisis.append(p)
            if len(choisis) != NB_RAYONS:
                avert.append('fenetres de la cloche ({} profils sur {})'.format(len(choisis), NB_RAYONS))
            extruder(choisis, 'MOT_z_flasque - 0.5 mm', 'MOT_ep_flasque + 1 mm',
                     OP.CutFeatureOperation, 'Fenetres_cloche', cloche)
        tenter('fenetres de la cloche', fenetres)

        def moyeu():
            s = esquisse('Esq_moyeu_cloche')
            cercle(s, D_MOYEU_CL, 'MOT_diam_moyeu_cloche')
            extruder(profils(s), 'MOT_z_flasque', 'MOT_ep_flasque + MOT_saillie_moyeu',
                     OP.JoinFeatureOperation, 'Moyeu_cloche', cloche)
        tenter('moyeu de la cloche', moyeu)

        # =====================================================================
        # 8. ARBRE : partie filetee M5 + partie lisse, bout creux
        # =====================================================================
        sk = esquisse('Esq_arbre')
        cercle(sk, D_ARBRE, 'MOT_diam_arbre')
        f = extruder(profils(sk), 'MOT_hauteur_corps + MOT_long_lisse', 'MOT_long_arbre - MOT_long_lisse',
                     OP.NewBodyFeatureOperation, 'Arbre_filete')
        arbre = f.bodies.item(0)
        arbre.name = 'Arbre'

        def filetage():
            tf = comp.features.threadFeatures
            info = tf.createThreadInfo(False, 'ISO Metric profile', 'M5x0.8', '6g')
            ti = tf.createInput(f.sideFaces.item(0), info)
            ti.isFullLength = True
            tf.add(ti).name = 'Filetage_M5'
        tenter('filetage M5 (cosmetique)', filetage)

        extruder(profils(sk), 'MOT_hauteur_corps', 'MOT_long_lisse',
                 OP.JoinFeatureOperation, 'Arbre_lisse', arbre)

        def creux():
            s = esquisse('Esq_creux_arbre')
            cercle(s, 2.4, '2.4 mm')
            extruder(profils(s), 'MOT_hauteur_totale - 3 mm', '3 mm',
                     OP.CutFeatureOperation, 'Creux_arbre', arbre)
        tenter('bout creux de l\'arbre', creux)

        # ---------- Fin ----------
        app.activeViewport.fit()
        msg = 'Moteur AI2807 cree.\n\nParametres : Modify > Change Parameters (MOT_...).'
        if avert:
            msg += '\n\nDetails non crees ou incomplets :\n - ' + '\n - '.join(avert)
        ui.messageBox(msg)
    except:
        if ui:
            txt = 'Echec du script :\n{}'.format(traceback.format_exc())
            if avert:
                txt += '\n\nAvertissements avant l\'echec : ' + ', '.join(avert)
            ui.messageBox(txt)
