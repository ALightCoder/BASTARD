# BASTARD - GPS Holybro Micro M10 avec boitier
# Script Fusion 360 : cree les parametres utilisateur, l'esquisse cotee et le corps.
# Cotes mesurees au pied a coulisse numerique (Mesure.pdf, 11/11/2026).
# Repere : X+ = sens de la fleche (avant), Y = largeur, Z+ = haut,
#          origine au centre de la face inferieure.

import adsk.core
import adsk.fusion
import traceback

# nom, valeur en mm, commentaire
PARAMETRES = [
    ('GPS_longueur',    34.45, 'Longueur, sens de la fleche - MESURE'),
    ('GPS_largeur',     27.93, 'Largeur - MESURE'),
    ('GPS_hauteur',     10.79, 'Hauteur / epaisseur - MESURE'),
    ('GPS_rayon_coin',   3.0,  'Rayon des coins vu de dessus - ESTIME sur photo'),
    ('GPS_rayon_arete',  0.8,  'Arrondi des aretes haut et bas - ESTIME sur photo'),
    ('GPS_prof_fleche',  0.3,  'Profondeur de la fleche de reperage - visuel'),
]


def run(context):
    ui = None
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

        # ---------- 1. Parametres utilisateur ----------
        up = design.userParameters
        for nom, val, com in PARAMETRES:
            expr = '{} mm'.format(val)
            p = up.itemByName(nom)
            if p:
                p.expression = expr
            else:
                up.add(nom, VI.createByString(expr), 'mm', com)

        # ---------- 2. Composant ----------
        root = design.rootComponent
        try:
            # Document d'assemblage : on cree un sous-composant
            occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
            comp = occ.component
        except:
            # Document "Part Design" (un seul composant autorise) : on dessine dans la racine
            comp = root
        try:
            comp.name = 'GPS_Holybro_Micro_M10'
        except:
            pass

        # ---------- 3. Esquisse du contour (plan XY) ----------
        sk = comp.sketches.add(comp.xYConstructionPlane)
        sk.name = 'Esquisse_contour_GPS'
        L, W = 3.445, 2.793  # cm (unite interne de l'API), pilote ensuite par les parametres
        lignes = sk.sketchCurves.sketchLines
        rect = lignes.addTwoPointRectangle(P3.create(-L / 2, -W / 2, 0), P3.create(L / 2, W / 2, 0))
        gc = sk.geometricConstraints
        dims = sk.sketchDimensions

        horiz, vert = [], []
        for i in range(rect.count):
            ln = rect.item(i)
            s, e = ln.startSketchPoint.geometry, ln.endSketchPoint.geometry
            if abs(s.y - e.y) < 1e-6:
                horiz.append(ln)
                try:
                    gc.addHorizontal(ln)
                except:
                    pass
            else:
                vert.append(ln)
                try:
                    gc.addVertical(ln)
                except:
                    pass

        # Diagonale de construction : son milieu est fixe sur l'origine -> rectangle centre
        bas = min(horiz, key=lambda l: l.startSketchPoint.geometry.y)
        haut = max(horiz, key=lambda l: l.startSketchPoint.geometry.y)

        def pt_gauche(l):
            a, b = l.startSketchPoint, l.endSketchPoint
            return a if a.geometry.x < b.geometry.x else b

        def pt_droit(l):
            a, b = l.startSketchPoint, l.endSketchPoint
            return a if a.geometry.x > b.geometry.x else b

        diag = lignes.addByTwoPoints(pt_gauche(bas), pt_droit(haut))
        diag.isConstruction = True
        gc.addMidPoint(sk.originPoint, diag)

        # Cotes pilotees par les parametres
        d1 = dims.addDistanceDimension(
            bas.startSketchPoint, bas.endSketchPoint,
            adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation,
            P3.create(0, -W / 2 - 0.6, 0))
        d1.parameter.expression = 'GPS_longueur'
        v = vert[0]
        d2 = dims.addDistanceDimension(
            v.startSketchPoint, v.endSketchPoint,
            adsk.fusion.DimensionOrientations.VerticalDimensionOrientation,
            P3.create(v.startSketchPoint.geometry.x * 1.4, 0, 0))
        d2.parameter.expression = 'GPS_largeur'

        # ---------- 4. Extrusion ----------
        ext = comp.features.extrudeFeatures.addSimple(
            sk.profiles.item(0), VI.createByString('GPS_hauteur'),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        ext.name = 'Extrusion_GPS'
        corps = ext.bodies.item(0)
        corps.name = 'GPS_Micro_M10'

        # ---------- 5. Conges ----------
        def conge(aretes, expr, nom):
            col = adsk.core.ObjectCollection.create()
            for a in aretes:
                col.add(a)
            ff = comp.features.filletFeatures
            fi = ff.createInput()
            try:
                fi.edgeSetInputs.addConstantRadiusEdgeSet(col, VI.createByString(expr), True)
            except:
                fi.addConstantRadiusEdgeSet(col, VI.createByString(expr), True)
            f = ff.add(fi)
            f.name = nom

        def etendue_z(a):
            bb = a.boundingBox
            return bb.maxPoint.z - bb.minPoint.z

        conge([a for a in corps.edges if etendue_z(a) > 1e-4],
              'GPS_rayon_coin', 'Conge_coins')
        conge([a for a in corps.edges if etendue_z(a) < 1e-6],
              'GPS_rayon_arete', 'Conge_aretes')

        # ---------- 6. Fleche de reperage (visuel, sens X+) ----------
        try:
            pi = comp.constructionPlanes.createInput()
            pi.setByOffset(comp.xYConstructionPlane, VI.createByString('GPS_hauteur'))
            plan = comp.constructionPlanes.add(pi)
            plan.name = 'Plan_dessus_GPS'
            sk2 = comp.sketches.add(plan)
            sk2.name = 'Esquisse_fleche'
            pts = [(0.55, 0.0), (0.15, 0.20), (0.25, 0.0), (0.15, -0.20)]  # cm
            l2 = sk2.sketchCurves.sketchLines
            prem = l2.addByTwoPoints(P3.create(pts[0][0], pts[0][1], 0), P3.create(pts[1][0], pts[1][1], 0))
            prec = prem
            for x, y in pts[2:]:
                prec = l2.addByTwoPoints(prec.endSketchPoint, P3.create(x, y, 0))
            l2.addByTwoPoints(prec.endSketchPoint, prem.startSketchPoint)
            coupe = comp.features.extrudeFeatures.addSimple(
                sk2.profiles.item(0), VI.createByString('-GPS_prof_fleche'),
                adsk.fusion.FeatureOperations.CutFeatureOperation)
            coupe.name = 'Gravure_fleche'
            plan.isLightBulbOn = False
        except:
            pass  # la fleche est decorative : le corps reste valide sans elle

        app.activeViewport.fit()
        ui.messageBox('GPS Micro M10 cree.\n\nParametres : Modifier > Modifier les parametres '
                      '(GPS_longueur, GPS_largeur, GPS_hauteur...)')
    except:
        if ui:
            ui.messageBox('Echec du script :\n{}'.format(traceback.format_exc()))
