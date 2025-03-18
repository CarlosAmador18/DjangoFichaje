from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model, logout
from django.contrib import messages
import requests
from django.views.generic import TemplateView
from django.http import HttpResponse
from datetime import datetime, timedelta
from django.http import JsonResponse
import json
from datetime import datetime
from django.utils.timezone import now

def validate_token(token):
    auth_token = request.COOKIES.get("auth_token")
    if auth_token:
        return True
    else:
        return False


def login_view(request):
    auth_token = request.COOKIES.get("auth_token")
    if auth_token:
        return redirect("fichar")
    else:
        if request.method == "POST":
            cod_usuario = request.POST.get("cod_usuario")
            clave_usuario = request.POST.get("clave_usuario")
            cod_empresa = request.POST.get("cod_empresa")
            cod_programa = "qcp"

            if not cod_usuario or not clave_usuario or not cod_empresa:
                messages.error(request, "Todos los campos son obligatorios.")
                return render(request, "fichar/index.html")

            api_url = "https://api.queryinformatica.com/v1/login"
            payload = {
                "cod_usuario": cod_usuario,
                "clave_usuario": clave_usuario,
                "cod_empresa": cod_empresa,
                "cod_programa": cod_programa,
            }

            try:
                response = requests.post(api_url, data=payload)
                print(f"Request payload: {payload}")
                print(f"Response status code: {response.status_code}")
                print(f"Response content: {response.content}")

                if response.status_code == 200:
                    data = response.json()
                    print(f"Response JSON: {data}")

                    if "success" in data and data["success"] == 1:
                        token = data.get("token")
                        num_instalacion = data.get("num_instalacion")
                        response = redirect("conexion")
                        response.set_cookie("auth_token", token, httponly=True)
                        response.set_cookie(
                            "num_instalacion", num_instalacion, httponly=True
                        )

                        User = get_user_model()
                        user, created = User.objects.get_or_create(username=cod_usuario)
                        login(request, user)

                        messages.success(request, "Login exitoso")
                        print("Login exitoso")
                        return response
                    else:
                        messages.error(request, "No se pudo autenticar con el API")

                else:
                    messages.error(request, f"Error de servidor: {response.status_code}")

            except requests.exceptions.RequestException as e:
                print(f"Request exception: {e}")
                messages.error(
                    request, "No se pudo autenticar debido a un error en la conexión."
                )

        return render(request, "fichar/index.html")


def logout_view(request):
    auth_token = request.COOKIES.get("auth_token")
    cod_programa = "qcp"

    if auth_token:
        api_url = "https://api.queryinformatica.com/v1/logout"
        payload = {"token": auth_token, "cod_programa": cod_programa}

        response = requests.post(api_url, data=payload)
        try:
            print(f"Request payload: {payload}")
            print(f"Response status code: {response.status_code}")
            print(f"Response content: {response.content}")

            if response.status_code == 200:
                data = response.json()
                print(f"Response JSON: {data}")

                if "success" in data and data["success"] == 1:
                    logout(request)
                    response = redirect("login")
                    response.delete_cookie("auth_token")
                    response.delete_cookie("num_instalacion")
                    messages.success(request, "Logout exitoso")
                    print("Logout exitoso")
                    return response
                elif "success" in data and data["success"] == 10:
                    logout(request)
                    response = redirect("login") 
                    response.delete_cookie("auth_token")
                    response.delete_cookie("num_instalacion")
                    
                else:
                    messages.error(request, "No se pudo cerrar sesión con el API")

            else:
                messages.error(request, f"Error de servidor: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Request exception: {e}")
            messages.error(
                request, "No se pudo cerrar sesión debido a un error en la conexión."
            )

    else:
        messages.error(request, "No hay sesión activa.")

    return redirect("login")


def obtener_conexion(request):
    auth_token = request.COOKIES.get("auth_token")
    cod_programa = "qcp"
    num_instalacion = request.COOKIES.get("num_instalacion")

    print(auth_token)
    print(cod_programa)
    print(num_instalacion)

    if auth_token:
        api_url = "https://api.queryinformatica.com/v1/config/conn/get-config"
        payload = {
            "token": auth_token,
            "cod_programa": cod_programa,
            "num_instalacion": num_instalacion,
        }

        try:
            response = requests.post(api_url, data=payload)

            if response.status_code == 200:
                data = response.json()
                print(f"Response JSON: {data}")

                if "success" in data and data["success"] == 1:
                    messages.success(request, "Conexión exitosa")
                    canal = data.get("CANAL")
                    id_usuario = data.get("ID_USUARIO")
                    print(id_usuario)
                    print(canal)
                    print("Conexión exitosa")
                    response = redirect("fichar")
                    response.set_cookie("canal", canal, httponly=True)

                    return response

                else:
                    messages.error(request, "No se pudo obtener la conexión con el API")

            else:
                messages.error(request, f"Error de servidor: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Request exception: {e}")
            messages.error(
                request,
                "No se pudo obtener la conexión debido a un error en la conexión.",
            )

    else:
        messages.error(request, "No hay sesión activa.")

    return HttpResponse(status=500)


def fichar(request):
    return render(request, "fichar/fichar.html")


def map(request):
    return render(request, "fichar/map.html")


def horario(request):
    return render(request, "fichar/horario.html")


def registro(request):
    if request.method == "POST":
        data = json.loads(request.body)
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        tipo = data.get("tipo")

        fecha = int(datetime.now().timestamp() * 1000)
        descripcion = data.get("descripcion")
        print(descripcion)
        canal = request.COOKIES.get("canal")
        auth_token = request.COOKIES.get("auth_token")
        cod_programa = "qcp"
        user_type = "client"
        action = "put_one"

        data_json = {
            "CANAL": canal,
            "FECHA": fecha,
            "TIPO": tipo,
            "LATITUD": latitude,
            "LONGITUD": longitude,
            "DESCRIPCION": descripcion,
        }

        if auth_token:
            api_url = "https://api.queryinformatica.com/v1/data/users/sign-action"

            payload = {
                "token": auth_token,
                "program_code": cod_programa,
                "user_type": user_type,
                "action": action,
                "data": json.dumps(data_json),
            }

            response = requests.post(api_url, data=payload)
            print(f"Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")

            if response.status_code == 200:
                data = response.json()
                print(f"Response JSON: {data}")

                if "success" in data and data["success"] == 1:
                    messages.success(request, "Registro exitoso")
                    print("Registro exitoso")
                    return redirect("fichar")
                else:
                    messages.error(request, "No se pudo registrar con el API")
            else:
                messages.error(request, f"Error de servidor: {response.status_code}")

        return JsonResponse({"message": "Data received"}, status=200)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)
    
def irregistros(request):
    return render(request, "fichar/registros.html")


def obtener_registros(request):
    registros = []
    auth_token = request.COOKIES.get("auth_token")
    cod_programa = "qcp" 
    user_type = "client"
    action = "get_last_records"

    if auth_token:
        api_url = "https://api.queryinformatica.com/v1/data/users/sign-action"

        payload = {
            "token": auth_token,
            "program_code": cod_programa,
            "user_type": user_type,
            "action": action,
        }

        try:
            response = requests.post(api_url, data=payload)

            if response.status_code == 200:
                data = response.json()

                if "success" in data and data["success"] == 1:
                    registros = data.get("data", [])

                    for registro in registros:
                        if "FECHA" in registro:
                            timestamp = int(registro["FECHA"]) / 1000
                            registro["FECHA"] = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                        tipo = int(registro["TIPO"])
                        if tipo == 0:
                            registro["TIPO"] = "Entrada"
                        elif tipo == 1:
                            registro["TIPO"] = "Salida"
                        else:
                            registro["TIPO"] = "Desconocido"
                else:
                    messages.error(request, "No se pudo obtener los registros con el API")
            else:
                messages.error(request, f"Error de servidor: {response.status_code}")
        except requests.exceptions.RequestException as e:
            messages.error(request, f"Error en la solicitud API: {e}")
    else:
        messages.error(request, "No se encontró el token de autenticación")

    return render(request, "fichar/registros.html", {"registros": registros})


def obtenerhorarios(request):
    registros = []
    registros_formateados = []

    auth_token = request.COOKIES.get("auth_token")
    filter_type = request.GET.get("filter", "day")
    cod_programa = "qcp"
    user_type = "client"
    action = "get_last_records"

    if not auth_token:
        return JsonResponse({"error": "No autenticado"}, status=401)

    api_url = "https://api.queryinformatica.com/v1/data/users/sign-action"

    payload = {
        "token": auth_token,
        "program_code": cod_programa,
        "user_type": user_type,
        "action": action,
    }

    try:
        response = requests.post(api_url, data=payload)

        if response.status_code == 200:
            data = response.json()

            if "success" in data and data["success"] == 1:
                registros_raw = data.get("data", [])
                
                today = datetime.now().date()
                
                for registro in registros_raw:
                    if "FECHA" in registro:
                        timestamp = int(registro["FECHA"]) / 1000
                        fecha_dt = datetime.fromtimestamp(timestamp)

                        include_record = False
                        
                        if filter_type == "day":
                            include_record = fecha_dt.date() == today
                        elif filter_type == "week":
                            days_diff = (today - fecha_dt.date()).days
                            include_record = 0 <= days_diff < 7
                        elif filter_type == "month":
                            include_record = (fecha_dt.month == today.month and 
                                             fecha_dt.year == today.year)
                        
                        if include_record:
                            fecha_formateada = fecha_dt.strftime('%Y-%m-%d %H:%M:%S')
                            tipo_valor = int(registro.get("TIPO", -1))

                            registro_formateado = {
                                "fecha": fecha_formateada,
                                "tipo": tipo_valor,
                                "descripcion": registro.get("DESCRIPCION", ""),
                                "latitud": registro.get("LATITUD", ""),
                                "longitud": registro.get("LONGITUD", "")
                            }

                            registros_formateados.append(registro_formateado)
                            
                registros_formateados.sort(key=lambda x: x["fecha"], reverse=True)
                
                return JsonResponse(registros_formateados, safe=False)
            else:
                return JsonResponse({"error": "Error en la respuesta de la API"}, status=500)
        else:
            return JsonResponse({"error": f"Error de servidor: {response.status_code}"}, status=500)
                
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud API: {e}")
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse(registros_formateados, safe=False)

