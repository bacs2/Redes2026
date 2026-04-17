import socket
from dnslib import DNSRecord
from dnslib.dns import CLASS, QTYPE
import dnslib

IP = "192.168.56.1"
BUFF_SIZE = 1024

servidor_raiz = "192.33.4.12"
cache = {}
historial_dns ={}  # (name, ip): frecuency


def actualizar_cache():
    # busca los 3 dominios más consultados en el historial y los guarda en la cache
    sorted_historial = sorted(historial_dns.items(), key=lambda item: item[1], reverse=True)
    top_3 = sorted_historial[:3]
    for (name, ip), freq in top_3:
        cache[name] = ip
        print(f"Actualizando cache: {name} -> {ip} (frecuencia: {freq})")

def parse_dns_reply_elements(dnslib_reply):
    # header section
    #>>--------------- HEADER SECTION ---------------<<\n")


    dns_message = {}
    dns_header = {}
    dns_query = []
    dns_answer = []
    dns_autority = []
    dns_aditional = []

    dns_message['header'] = dns_header
    dns_message['query'] = dns_query
    dns_message['answer'] = dns_answer
    dns_message['authority'] = dns_autority
    dns_message['additional'] = dns_aditional


    qr_flag = dnslib_reply.header.get_qr()
    number_of_query_elements = dnslib_reply.header.q
    number_of_answer_elements = dnslib_reply.header.a
    number_of_authority_elements = dnslib_reply.header.auth
    number_of_additional_elements = dnslib_reply.header.ar
    
    dns_header["ANCOUNT"] = number_of_answer_elements
    dns_header["NSCOUNT"] = number_of_authority_elements
    dns_header["ARCOUNT"] = number_of_additional_elements




    #>>---------------- QUERY SECTION ---------------<<\n")
    all_querys = dnslib_reply.questions  # lista de objetos tipo dnslib.dns.DNSQuestion
    for query in all_querys:
        q_dict = {
            'qname': query.get_qname(),
            'qclass': CLASS.get(query.qclass),
            'qtype': QTYPE.get(query.qtype)
        }
        dns_query.append(q_dict)

    #>>---------------- ANSWER SECTION --------------<<\n")
    if number_of_answer_elements > 0:
        for answer in dnslib_reply.rr:
            a_dict = {
                'rname': answer.get_rname(),
                'rclass': CLASS.get(answer.rclass),
                'rtype': QTYPE.get(answer.rtype),
                'ttl': answer.ttl,
                'rdata': answer.rdata
            }
            dns_answer.append(a_dict)


    #>>-------------- AUTHORITY SECTION -------------<<\n")
    # authority section
    if number_of_authority_elements > 0:
        authority_section_list = dnslib_reply.auth
        for auth in authority_section_list:
            auth_dict = {
                'rname': auth.get_rname(),
                'auth_type': QTYPE.get(auth.rtype),
                'auth_class': CLASS.get(auth.rclass),
                'auth_time_to_live': auth.ttl,
                'rdata': auth.rdata
            }
            dns_autority.append(auth_dict)

    #>>------------- ADDITIONAL SECTION -------------<<
    if number_of_additional_elements > 0:
        additional_records = dnslib_reply.ar
        for ar in additional_records:
            ar_dict = {
                'rname': ar.get_rname(),
                'ar_type': QTYPE.get(ar.rtype),
                'ar_class': CLASS.get(ar.rclass),
                'ttl': ar.ttl,
                'rdata': ar.rdata
            }
            dns_aditional.append(ar_dict)


    return dns_message




def resolver(query, ip=servidor_raiz):

    
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    qname = query["qname"]
    q = DNSRecord.question(qname)
    print('(debug) Consultando {} con ip: {}'.format(qname,ip ))



    #chequear si qname esta en el cache   
    if str(qname) in cache:
        ip_resuelta = cache[str(qname)]
        print(f"(debug) Cache encontrado: {qname} -> {ip_resuelta}")
        reply = q.reply()
        reply.header.aa = 0 # No es autoritativo, solo responde desde cache
        reply.add_answer(dnslib.RR(qname, rtype=QTYPE.A, rclass=1, ttl=300, rdata=dnslib.A(ip_resuelta)))
        return reply    
    try:
        # a.- Enviar query al servidor y esperar respuesta en el puerto 53
        client.sendto(bytes(q.pack()), (ip, 53))
        data, _ = client.recvfrom(BUFF_SIZE)
    except socket.timeout:
        client.close()
        return None
    client.close()

    parsed_reply = DNSRecord.parse(data)
    dns_dict = parse_dns_reply_elements(parsed_reply)

    # b.- Revisar si hay respuesta tipo A en Answer
    for ans in dns_dict['answer']:
        if ans['rtype'] == 'A':

            ip_resuelta = str(ans['rdata'])
            clave = (str(qname), ip_resuelta)
            
            if clave in historial_dns:
                historial_dns[clave] += 1
            else:
                historial_dns[clave] = 1
                
            return parsed_reply

    # c.- Revisar delegación de Name Server en Authority
    ns_found = False
    for auth in dns_dict['authority']:
        if auth['auth_type'] == 'NS':
            ns_found = True
            break
            
    if ns_found:
        # i.- Revisar si hay respuesta tipo A en Additional
        ip_additional = None
        for adr in dns_dict['additional']:
            if adr['ar_type'] == 'A':
                ip_additional = str(adr['rdata'])
                break
                
        if ip_additional:
            # Enviar query original a la IP contenida en Additional
            return resolver(query, ip_additional)
        else:
            # ii.- Tomar nombre del Name Server y resolver su IP recursivamente
            for auth in dns_dict['authority']:
                if auth['auth_type'] == 'NS':
                    ns_name = str(auth['rdata'])
                    ns_query_record = DNSRecord.question(ns_name)
                    
                    # Usamos el parser ya creado para generar el diccionario de la query
                    ns_query_dict = parse_dns_reply_elements(ns_query_record)['query'][0]
                    
                    # Resolver IP del Name Server partiendo desde la raíz
                    ns_reply = resolver(ns_query_dict, servidor_raiz)
                    if ns_reply:
                        ns_reply_dict = parse_dns_reply_elements(ns_reply)
                        ip_ns = None
                        for ans in ns_reply_dict['answer']:
                            if ans['rtype'] == 'A':
                                ip_ns = str(ans['rdata'])
                                break
                        
                        # Si se obtuvo la IP del NS, reenviamos la query original a este paso
                        if ip_ns:
                            return resolver(query, ip_ns)
                    break
    
    return parsed_reply



if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_adress = (IP, 8000)
    server.bind(server_adress)
    print(f"socket escuchando en {IP}:{8000}")

    while True:
        mensaje_bytes, client_address = server.recvfrom(BUFF_SIZE)
        print(f"mensaje recibido de {client_address}")
        print(mensaje_bytes)


        mensaje =DNSRecord.parse(mensaje_bytes)
        id_mensaje = mensaje.header.id
        mensaje_parseado = parse_dns_reply_elements(mensaje)
        querys = mensaje_parseado['query']
        for query in querys:
            parsed_reply = resolver(query)
            if parsed_reply:
                # Retornar la respuesta al cliente
                parsed_reply.header.id = id_mensaje  # mantener el mismo ID en la respuesta
                parsed_reply.header.set_qr(1)  # marcar como respuesta
                parsed_reply.header.set_ra(1)  # indicar que soportamos recursividad
                parsed_reply.header.aa = 0     # no somos servidor autoritativo
                print("mensaje recibido: {}".format(parsed_reply))
                actualizar_cache()
                server.sendto(bytes(parsed_reply.pack()), client_address)

        print("mensaje enviado a {}: {}".format(client_address, parsed_reply))
        print("--------------------------------------------------")    


    


