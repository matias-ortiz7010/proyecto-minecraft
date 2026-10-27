from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import JugadorForm, ModForm, ServidorForm, SpeedrunForm
from .models import Jugador, Mod, PvP, Servidor, Speedrun


def index(request):
    speedruns = Speedrun.objects.select_related("jugador")[:5]
    servidores = Servidor.objects.all()[:10]
    mods = Mod.objects.all()[:6]
    top_pvp = PvP.objects.select_related("jugador").order_by("-victorias", "-kills").first()

    record = speedruns[0] if speedruns else None
    top_server = servidores[0] if servidores else None
    top_mod = mods[0] if mods else None

    context = {
        "speedruns": speedruns,
        "servidores": servidores,
        "mods": mods,
        "record": record,
        "top_pvp": top_pvp,
        "top_server": top_server,
        "top_mod": top_mod,
        "chart_labels": [run.jugador.nombre for run in speedruns],
        "chart_values": [round(run.tiempo_ms / 1000, 3) for run in speedruns],
    }
    return render(request, "index.html", context)


def api_buscar_jugador(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse({"ok": False, "error": "Escribí el nombre de un jugador."}, status=400)

    jugador = (
        Jugador.objects.filter(Q(nombre__iexact=query) | Q(uuid__iexact=query))
        .select_related("pvp")
        .first()
    )
    if not jugador:
        return JsonResponse({"ok": False, "error": "Jugador no encontrado."}, status=404)

    try:
        pvp = jugador.pvp
    except PvP.DoesNotExist:
        pvp = None

    mejor_speedrun = jugador.speedruns.order_by("tiempo_ms").first()

    return JsonResponse(
        {
            "ok": True,
            "jugador": {
                "nombre": jugador.nombre,
                "uuid": jugador.uuid,
                "pais": jugador.pais,
                "skin_url": jugador.skin_url,
                "pvp": {
                    "victorias": pvp.victorias,
                    "derrotas": pvp.derrotas,
                    "kills": pvp.kills,
                    "racha": pvp.racha,
                    "winrate": pvp.winrate,
                } if pvp else None,
                "mejor_speedrun": {
                    "categoria": mejor_speedrun.categoria,
                    "tiempo": mejor_speedrun.tiempo_formateado,
                    "version": mejor_speedrun.version,
                    "verificado": mejor_speedrun.verificado,
                } if mejor_speedrun else None,
            },
        }
    )


def api_resumen(request):
    record = Speedrun.objects.select_related("jugador").first()
    top_pvp = PvP.objects.select_related("jugador").order_by("-victorias", "-kills").first()
    top_server = Servidor.objects.first()
    top_mod = Mod.objects.first()

    return JsonResponse(
        {
            "record": {
                "jugador": record.jugador.nombre,
                "tiempo": record.tiempo_formateado,
            } if record else None,
            "jugador_top": top_pvp.jugador.nombre if top_pvp else None,
            "servidor_top": top_server.nombre if top_server else None,
            "mod_top": top_mod.nombre if top_mod else None,
        }
    )


def api_servidores(request):
    data = [
        {
            "id": servidor.id,
            "nombre": servidor.nombre,
            "ip": servidor.ip,
            "pais": servidor.pais,
            "jugadores": servidor.jugadores,
            "online": servidor.online,
            "actualizado_en": servidor.actualizado_en.isoformat(),
        }
        for servidor in Servidor.objects.all()[:50]
    ]
    return JsonResponse({"servidores": data})


def api_speedruns(request):
    data = [
        {
            "id": run.id,
            "jugador": run.jugador.nombre,
            "categoria": run.categoria,
            "tiempo": run.tiempo_formateado,
            "tiempo_ms": run.tiempo_ms,
            "fecha": run.fecha.isoformat() if run.fecha else None,
            "version": run.version,
            "verificado": run.verificado,
            "fuente_url": run.fuente_url,
        }
        for run in Speedrun.objects.select_related("jugador")[:50]
    ]
    return JsonResponse({"speedruns": data})


def api_mods(request):
    data = [
        {
            "id": mod.id,
            "nombre": mod.nombre,
            "autor": mod.autor,
            "version": mod.version,
            "descargas": mod.descargas,
            "url": mod.url,
        }
        for mod in Mod.objects.all()[:50]
    ]
    return JsonResponse({"mods": data})


# -----------------------------
# ABM de jugadores
# -----------------------------

@staff_member_required(login_url="stats:gestion_login")
def jugadores_gestion(request):
    """Listado/consulta del ABM de jugadores."""
    query = request.GET.get("q", "").strip()
    jugadores = Jugador.objects.all()
    if query:
        jugadores = jugadores.filter(
            Q(nombre__icontains=query)
            | Q(uuid__icontains=query)
            | Q(pais__icontains=query)
        )

    return render(
        request,
        "gestion/jugadores/lista.html",
        {"jugadores": jugadores, "query": query},
    )


@staff_member_required(login_url="stats:gestion_login")
def jugador_crear(request):
    """Alta de un jugador."""
    form = JugadorForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        jugador = form.save()
        messages.success(request, f"Jugador {jugador.nombre} agregado correctamente.")
        return redirect("stats:jugadores_gestion")

    return render(
        request,
        "gestion/jugadores/form.html",
        {"form": form, "titulo": "Agregar jugador", "accion": "Crear jugador"},
    )


@staff_member_required(login_url="stats:gestion_login")
def jugador_editar(request, pk):
    """Modificación de un jugador existente."""
    jugador = get_object_or_404(Jugador, pk=pk)
    form = JugadorForm(request.POST or None, instance=jugador)
    if request.method == "POST" and form.is_valid():
        jugador = form.save()
        messages.success(request, f"Jugador {jugador.nombre} actualizado correctamente.")
        return redirect("stats:jugadores_gestion")

    return render(
        request,
        "gestion/jugadores/form.html",
        {
            "form": form,
            "titulo": f"Editar {jugador.nombre}",
            "accion": "Guardar cambios",
            "jugador": jugador,
        },
    )


@staff_member_required(login_url="stats:gestion_login")
def jugador_eliminar(request, pk):
    """Baja de un jugador. La eliminación final solo se ejecuta por POST."""
    jugador = get_object_or_404(Jugador, pk=pk)
    if request.method == "POST":
        nombre = jugador.nombre
        jugador.delete()
        messages.success(request, f"Jugador {nombre} eliminado correctamente.")
        return redirect("stats:jugadores_gestion")

    return render(
        request,
        "gestion/jugadores/confirmar_eliminar.html",
        {"jugador": jugador},
    )


# -----------------------------
# ABM de servidores
# -----------------------------

@staff_member_required(login_url="stats:gestion_login")
def servidores_gestion(request):
    """Consulta/listado y búsqueda por nombre, IP/dominio o país."""
    query = request.GET.get("q", "").strip()
    servidores = Servidor.objects.all()
    if query:
        servidores = servidores.filter(
            Q(nombre__icontains=query)
            | Q(ip__icontains=query)
            | Q(pais__icontains=query)
        )
    return render(
        request,
        "gestion/servidores/lista.html",
        {"servidores": servidores, "query": query},
    )


@staff_member_required(login_url="stats:gestion_login")
def servidor_crear(request):
    """Alta de servidor en la base de datos."""
    form = ServidorForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        servidor = form.save()
        messages.success(request, f"Servidor {servidor.nombre} agregado correctamente.")
        return redirect("stats:servidores_gestion")
    return render(
        request,
        "gestion/servidores/form.html",
        {"form": form, "titulo": "Agregar servidor", "accion": "Crear servidor"},
    )


@staff_member_required(login_url="stats:gestion_login")
def servidor_editar(request, pk):
    """Modificación de un servidor existente."""
    servidor = get_object_or_404(Servidor, pk=pk)
    form = ServidorForm(request.POST or None, instance=servidor)
    if request.method == "POST" and form.is_valid():
        servidor = form.save()
        messages.success(request, f"Servidor {servidor.nombre} actualizado correctamente.")
        return redirect("stats:servidores_gestion")
    return render(
        request,
        "gestion/servidores/form.html",
        {
            "form": form, "titulo": f"Editar {servidor.nombre}",
            "accion": "Guardar cambios", "servidor": servidor,
        },
    )


@staff_member_required(login_url="stats:gestion_login")
def servidor_eliminar(request, pk):
    """Baja de servidor; solo permite eliminar con confirmación por POST."""
    servidor = get_object_or_404(Servidor, pk=pk)
    if request.method == "POST":
        nombre = servidor.nombre
        servidor.delete()
        messages.success(request, f"Servidor {nombre} eliminado correctamente.")
        return redirect("stats:servidores_gestion")
    return render(
        request, "gestion/servidores/confirmar_eliminar.html",
        {"servidor": servidor},
    )


# -----------------------------
# ABM de mods
# -----------------------------

@staff_member_required(login_url="stats:gestion_login")
def mods_gestion(request):
    """Listado y búsqueda por nombre, autor y versión."""
    query = request.GET.get("q", "").strip()
    mods = Mod.objects.all()
    if query:
        mods = mods.filter(
            Q(nombre__icontains=query)
            | Q(autor__icontains=query)
            | Q(version__icontains=query)
        )
    return render(request, "gestion/mods/lista.html", {"mods": mods, "query": query})


@staff_member_required(login_url="stats:gestion_login")
def mod_crear(request):
    """Alta de un mod con validación mediante ModelForm."""
    form = ModForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        mod = form.save()
        messages.success(request, f"Mod {mod.nombre} agregado correctamente.")
        return redirect("stats:mods_gestion")
    return render(
        request, "gestion/mods/form.html",
        {"form": form, "titulo": "Agregar mod", "accion": "Crear mod"},
    )


@staff_member_required(login_url="stats:gestion_login")
def mod_editar(request, pk):
    """Modificación de un mod existente."""
    mod = get_object_or_404(Mod, pk=pk)
    form = ModForm(request.POST or None, instance=mod)
    if request.method == "POST" and form.is_valid():
        mod = form.save()
        messages.success(request, f"Mod {mod.nombre} actualizado correctamente.")
        return redirect("stats:mods_gestion")
    return render(
        request, "gestion/mods/form.html",
        {"form": form, "titulo": f"Editar {mod.nombre}", "accion": "Guardar cambios", "mod": mod},
    )


@staff_member_required(login_url="stats:gestion_login")
def mod_eliminar(request, pk):
    """Baja: GET presenta confirmación; POST elimina el registro."""
    mod = get_object_or_404(Mod, pk=pk)
    if request.method == "POST":
        nombre = mod.nombre
        mod.delete()
        messages.success(request, f"Mod {nombre} eliminado correctamente.")
        return redirect("stats:mods_gestion")
    return render(request, "gestion/mods/confirmar_eliminar.html", {"mod": mod})


# -----------------------------
# ABM de speedruns
# -----------------------------

@staff_member_required(login_url="stats:gestion_login")
def speedruns_gestion(request):
    """Listado ordenado por tiempo y búsqueda por jugador, categoría o versión."""
    query = request.GET.get("q", "").strip()
    speedruns = Speedrun.objects.select_related("jugador").all()
    if query:
        speedruns = speedruns.filter(
            Q(jugador__nombre__icontains=query)
            | Q(categoria__icontains=query)
            | Q(version__icontains=query)
        )
    return render(request, "gestion/speedruns/lista.html", {"speedruns": speedruns, "query": query})


@staff_member_required(login_url="stats:gestion_login")
def speedrun_crear(request):
    """Alta de speedrun asociada a un jugador existente."""
    form = SpeedrunForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        record = form.save()
        messages.success(request, f"Speedrun de {record.jugador.nombre} agregada correctamente.")
        return redirect("stats:speedruns_gestion")
    return render(
        request, "gestion/speedruns/form.html",
        {"form": form, "titulo": "Agregar speedrun", "accion": "Crear speedrun"},
    )


@staff_member_required(login_url="stats:gestion_login")
def speedrun_editar(request, pk):
    """Modificación de speedrun con validación de duración."""
    record = get_object_or_404(Speedrun, pk=pk)
    form = SpeedrunForm(request.POST or None, instance=record)
    if request.method == "POST" and form.is_valid():
        record = form.save()
        messages.success(request, f"Speedrun de {record.jugador.nombre} actualizada correctamente.")
        return redirect("stats:speedruns_gestion")
    return render(
        request, "gestion/speedruns/form.html",
        {"form": form, "titulo": "Editar speedrun", "accion": "Guardar cambios", "record": record},
    )


@staff_member_required(login_url="stats:gestion_login")
def speedrun_eliminar(request, pk):
    """Baja confirmada mediante POST (nunca borra desde un enlace GET)."""
    record = get_object_or_404(Speedrun.objects.select_related("jugador"), pk=pk)
    if request.method == "POST":
        nombre = record.jugador.nombre
        record.delete()
        messages.success(request, f"Speedrun de {nombre} eliminada correctamente.")
        return redirect("stats:speedruns_gestion")
    return render(request, "gestion/speedruns/confirmar_eliminar.html", {"record": record})
