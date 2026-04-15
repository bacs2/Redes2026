import socket
from dnslib import DNSRecord
from dnslib.dns import CLASS, QTYPE
import dnslib

IP = "192.168.56.101"
BUFF_SIZE = 1024

servidor_raiz = "192.33.4.12"



def print_dns_reply_elements(dnslib_reply):
    # header section
    print(">>--------------- HEADER SECTION ---------------<<\n")
    print("----------- dnslib_reply.header -----------\n{}\n".format(dnslib_reply.header))


    dns_message = {}
    dns_header = {}
    dns_query = {}
    dns_answer = {}
    dns_autority = {}
    dns_aditional = {}

    dns_message['header'] = dns_header
    dns_message['query'] = dns_query
    dns_message['answer'] = dns_answer
    dns_message['authority'] = dns_autority
    dns_message['additional'] = dns_aditional


    qr_flag = dnslib_reply.header.get_qr()
    print("-> qr_flag = {}".format(qr_flag))

    number_of_query_elements = dnslib_reply.header.q
    print("-> number_of_query_elements = {}".format(number_of_query_elements))

    number_of_answer_elements = dnslib_reply.header.a
    print("-> number_of_answer_elements = {}".format(number_of_answer_elements))

    number_of_authority_elements = dnslib_reply.header.auth
    print("-> number_of_authority_elements = {}".format(number_of_authority_elements))

    number_of_additional_elements = dnslib_reply.header.ar
    print("-> number_of_additional_elements = {}".format(number_of_additional_elements))
    
    dns_header["ANCOUNT"] = number_of_answer_elements
    dns_header["NSCOUNT"] = number_of_authority_elements
    dns_header["ARCOUNT"] = number_of_additional_elements




    print(">>---------------- QUERY SECTION ---------------<<\n")
    # query section
    all_querys = dnslib_reply.questions  # lista de objetos tipo dnslib.dns.DNSQuestion
    first_query = dnslib_reply.get_q()  # primer objeto en la lista all_querys
    domain_name_in_query = first_query.get_qname()  # nombre de dominio por el cual preguntamos
    query_class = CLASS.get(first_query.qclass)
    query_type = QTYPE.get(first_query.qtype)


    dns_query['qname'] = domain_name_in_query
    dns_query['qclass'] = query_class
    dns_query['qtype'] = query_type
    print(">>----------------------------------------------<<\n")

    print(">>---------------- ANSWER SECTION --------------<<\n")
    # answer section
    if number_of_answer_elements > 0:
        all_resource_records = dnslib_reply.rr  # lista de objetos tipo dnslib.dns.RR

        first_answer = dnslib_reply.get_a()  # primer objeto en la lista all_resource_records
        domain_name_in_answer = first_answer.get_rname()  # nombre de dominio por el cual se está respondiendo
        answer_class = CLASS.get(first_answer.rclass)
        answer_type = QTYPE.get(first_answer.rtype)
        answer_rdata = first_answer.rdata  # rdata asociada a la respuesta

            
        dns_answer['rname'] = domain_name_in_answer
        dns_answer['rclass'] = answer_class
        dns_answer['rtype'] = answer_type
        dns_answer['rdata'] = answer_rdata
    else:
        print("-> number_of_answer_elements = {}".format(number_of_answer_elements))


    print(">>----------------------------------------------<<\n")

    print(">>-------------- AUTHORITY SECTION -------------<<\n")
    # authority section
    if number_of_authority_elements > 0:
        authority_section_list = dnslib_reply.auth  # contiene un total de number_of_authority_elements
        print("-> authority_section_list = {}".format(authority_section_list))

        if len(authority_section_list) > 0:
            authority_section_RR_0 = authority_section_list[0]  # objeto tipo dnslib.dns.RR
            auth_type = QTYPE.get(authority_section_RR_0.rtype)
            auth_class = CLASS.get(authority_section_RR_0.rclass)
            auth_time_to_live = authority_section_RR_0.ttl
            authority_section_0_rdata = authority_section_RR_0.rdata

            dns_autority['number_of_authority_elements'] = number_of_authority_elements
            dns_autority['auth_type'] = auth_type
            dns_autority['auth_class'] = auth_class
            dns_autority['auth_time_to_live'] = auth_time_to_live

            # si recibimos auth_type = 'SOA' este es un objeto tipo dnslib.dns.SOA
            if isinstance(authority_section_0_rdata, dnslib.dns.SOA):
                primary_name_server = authority_section_0_rdata.get_mname()  # servidor de nombre primario

            elif isinstance(authority_section_0_rdata, dnslib.dns.NS): # si en vez de SOA recibimos un registro tipo NS
                name_server_domain = authority_section_0_rdata  # entonces authority_section_0_rdata contiene el nombre de dominio del primer servidor de nombre de la lista
    else:

    print(">>------------- ADDITIONAL SECTION -------------<<\n")
    if number_of_additional_elements > 0:
        additional_records = dnslib_reply.ar  # lista que contiene un total de number_of_additional_elements DNS records

        first_additional_record = additional_records[0]  # objeto tipo dnslib.dns.RR

        # En caso de tener additional records, estos pueden contener la IP asociada a elementos del authority section
        ar_class = CLASS.get(first_additional_record.rclass)
        ar_type = QTYPE.get(first_additional_record.rclass)  # para saber si esto es asi debemos revisar el tipo de record

        if ar_type == 'A': # si el tipo es 'A' (Address)
            first_additional_record_rname = first_additional_record.rname  # nombre de dominio
            print("-> first_additional_record_rname = {}".format(first_additional_record_rname))

            first_additional_record_rdata = first_additional_record.rdata  # IP asociada
            print("-> first_additional_record_rdata = {}".format(first_additional_record_rdata))
    
        dns_aditional['ar_class'] = ar_class
        dns_aditional['ar_type'] = ar_type
    else:
        print("-> number_of_additional_elements = {}".format(number_of_additional_elements))
    print(">>----------------------------------------------<<\n")


    return dns_message




def obtener_mensaje_dns():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_adress = (IP, 8000)

    server.bind(server_adress)
    print(f"socket escuchando en {IP}:{8000}")

    while True:
        mensaje, client_address = server.recvfrom(BUFF_SIZE)
        print(f"mensaje recibido de {client_address}")
        print(mensaje)
        server.close()
        return mensaje

    # recibe un diccionario de la query 

def send_dns_message(message,address, port):
     # Acá ya no tenemos que crear el encabezado porque dnslib lo hace por nosotros, por default pregunta por el tipo A
    qname = message["qname"]
    q = DNSRecord.question(qname)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (address, port)
    try:
        # lo enviamos, hacemos cast a bytes de lo que resulte de la función pack() sobre el mensaje
        sock.sendto(bytes(q.pack()), server_address)
        # En data quedará la respuesta a nuestra consulta
        data, _ = sock.recvfrom(4096)
        # le pedimos a dnslib que haga el trabajo de parsing por nosotros 
        d = print_dns_reply_elements(DNSRecord.parse(data))

        if d['rtype'] == 'A':
            print("La IP asociada a {} es {}".format(d['rname'], d['rdata']))
            return message
        
        if 
        


    finally:
        sock.close()
    # Ojo que los datos de la respuesta van en en una estructura de datos
    return d 

def resolver(mensaje_consulta):
    qname = mensaje_consulta["qname"]
    print("resolviendo consulta por el dominio: {}".format(qname))

    q = DNSRecord.question(qname)
    server_address = (servidor_raiz, 53)




if __name__ == "__main__":
    mensaje = obtener_mensaje_dns()
    resolver(mensaje.reply.questions)
             

