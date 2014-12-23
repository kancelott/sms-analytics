#!/usr/bin/env python

########################################################
#
# SMS Analytics
# Author: kancelotto
#
# Designed to read XML files from the Android app 
# `SMS Backup & Restore' by Ritesh Sahu.
#
########################################################

import xml.etree.ElementTree as ET
import operator
import sys
from datetime import datetime

def main():
    # ***** OPTIONS FOR YOUR TINKERING *****
    # xml file name
    sms_file = sys.argv[1]

    # filter options
    is_year_filter_on = True
    year_filter = '2014'
    is_person_filter_on = True
    person_filter = 'Peter Phan'

    # to reduce noise in ratio calculations (people you text one off)
    ratio_min_texts = 20

    # display top n contacts
    top_contacts_limit = 20
    ratio_contacts_limit = 5

    # ************************************** 

    # load xml
    if is_year_filter_on:
        print 'SMS Analytics for %s by kancelotto' % (year_filter)
    else:
        print 'SMS Analytics for ALL TIME by kancelotto'
    print 'Crunching data... nomnomnom\n'
    tree = ET.parse(sms_file)
    root = tree.getroot()

    # CALCULATE TOTAL/RECEIVED/SENT SMSs
    total = 0
    recv = 0
    recv_percent = 0
    sent = 0
    sent_percent = 0
    for msg in root:
        # filter by year
        if is_year_filter_on:
            unix_date = int(msg.attrib['date']) / 1000
            year = datetime.fromtimestamp(unix_date).strftime('%Y')
            if year != year_filter: continue

        if msg.attrib['type'] == '1':
            recv += 1
        else:
            sent += 1
    total = recv + sent
    if total != 0:
        sent_percent = float(sent) / total * 100
        recv_percent = float(recv) / total * 100
    print 'Total SMSs:\t\t\t%5d\t100.00%%' % (total)
    print '\tSent:    \t\t%5d\t%6.2f%%' % (sent, sent_percent)
    print '\tReceived:\t\t%5d\t%6.2f%%' % (recv, recv_percent)
    print

    # CALCULATE TOP CONTACTS
    contacts = {}
    culm_sms = 0
    culm_percent = 0

    contacts_sent = {}
    culm_sms_sent = 0
    culm_percent_sent = 0

    contacts_recv = {}
    culm_sms_recv = 0
    culm_percent_recv = 0

    for msg in root:
        person = msg.attrib['contact_name']
        unix_date = int(msg.attrib['date']) / 1000

        # filter by year
        if is_year_filter_on:
            year = datetime.fromtimestamp(unix_date).strftime('%Y')
            if year != year_filter: continue

        # increment SMS count for this person
        if person in contacts:
            contacts[person] += 1
        else:
            contacts[person] = 1

        if person not in contacts_recv:
            contacts_recv[person] = 0
        if person not in contacts_sent:
            contacts_sent[person] = 0

        # increment SMS count for sent/received texts
        if msg.attrib['type'] == '1':
            contacts_recv[person] += 1
        else:
            contacts_sent[person] += 1

    # calculate sent-to-received ratios
    # exclude those below ratio_min_texts (noise reduction)
    sr_ratio = {}
    for person in contacts:
        if contacts[person] < ratio_min_texts: continue
        if contacts_recv[person] == 0:
            sr_ratio[person] = float('inf')
        else:
            sr_ratio[person] = float(contacts_sent[person]) / contacts_recv[person]

    # calculate received-to-sent ratios
    # exclude those below ratio_min_texts (noise reduction)
    rs_ratio = {}
    for person in contacts:
        if contacts[person] < ratio_min_texts: continue
        if contacts_sent[person] == 0:
            rs_ratio[person] = float('inf')
        else:
            rs_ratio[person] = float(contacts_recv[person]) / contacts_sent[person]

    # print stuff
    print 'Top contacts:'
    count = 1
    for person in sorted(contacts, key=contacts.get, reverse=True):
        percent = float(contacts[person]) / total * 100
        culm_sms += contacts[person]
        culm_percent += percent

        print '%6d\t%s' % (count, person),
        if len(person) < 15: print '       ',
        print '\t%5d\t%6.2f%%' % (contacts[person], percent)
        count += 1
        if count > top_contacts_limit:
            print '\tOthers        \t\t%5d\t%6.2f%%' % \
                    (total - culm_sms, 100 - culm_percent)
            break
    print

    print 'Sent-to-received ratios: (higher means you send texts to them all the time)'
    count = 1
    for person in sorted(sr_ratio, key=sr_ratio.get, reverse=True):
        print '%6d\t%s' % (count, person),
        if len(person) < 15: print '       ',
        print '\t%5.2f\t(%4d / %4d)' % (sr_ratio[person], contacts_sent[person],
                contacts_recv[person])
        count += 1
        if count > ratio_contacts_limit:
            break
    print

    print 'Received-to-sent ratios: (higher means they send you texts all the time)'
    count = 1
    for person in sorted(rs_ratio, key=rs_ratio.get, reverse=True):
        print '%6d\t%s' % (count, person),
        if len(person) < 15: print '       ',
        print '\t%5.2f\t(%4d / %4d)' % (rs_ratio[person], contacts_recv[person],
                contacts_sent[person])
        count += 1
        if count > ratio_contacts_limit:
            break
    print

    # CALCULATE MONTHLY/DAILY/HOURLY SMS ACTIVITY
    months = {}
    days = {}
    hours = {}
    month_names = {1: 'January:',
            2: 'February:',
            3: 'March:  ',
            4: 'April:  ',
            5: 'May:    ',
            6: 'June:   ',
            7: 'July:   ',
            8: 'August: ',
            9: 'September:',
            10: 'October:', 
            11: 'November:',
            12: 'December:'}
    day_names = {0: 'Sunday: ',
            1: 'Monday: ',
            2: 'Tuesday:',
            3: 'Wednesday:',
            4: 'Thursday:',
            5: 'Friday: ',
            6: 'Saturday:'}

    # initialise dictionaries
    for i in xrange(1, 13):
        months[i] = 0
    for i in xrange(0, 7):
        days[i] = 0
    for i in xrange(0, 24):
        hours[i] = 0

    for msg in root:
        person = msg.attrib['contact_name']
        unix_date = int(msg.attrib['date']) / 1000

        # filter by person
        if is_person_filter_on:
            if person != person_filter: continue

        # filter by year
        if is_year_filter_on:
            unix_date = int(msg.attrib['date']) / 1000
            year = datetime.fromtimestamp(unix_date).strftime('%Y')
            if year != year_filter: continue

        # filter by month
        month = int(datetime.fromtimestamp(unix_date).strftime('%m'))

        # filter by day
        day = int(datetime.fromtimestamp(unix_date).strftime('%w'))

        # filter by hour
        hour = int(datetime.fromtimestamp(unix_date).strftime('%H'))

        # increment SMS counts
        months[month] += 1
        days[day] += 1
        hours[hour] += 1

    # calculate graph blocks
    max_block_length = 35
    month_seg = max(months.iteritems(), key=operator.itemgetter(1))[1] / \
            float(max_block_length)
    if month_seg == 0: month_seg = 1
    month_blocks = {}
    for month in months:
        month_blocks[month] = int(months[month] / month_seg + 0.5)

    day_seg = max(days.iteritems(), key=operator.itemgetter(1))[1] / \
            float(max_block_length)
    if day_seg == 0: day_seg = 1
    day_blocks = {}
    for day in days:
        day_blocks[day] = int(days[day] / day_seg + 0.5)

    hour_seg = max(hours.iteritems(), key=operator.itemgetter(1))[1] / \
            float(max_block_length)
    if hour_seg == 0: hour_seg = 1
    hour_blocks = {}
    for hour in hours:
        hour_blocks[hour] = int(hours[hour] / hour_seg + 0.5)

    # print stuff
    if is_person_filter_on:
        filter_sent_percent = 0
        filter_recv_percent = 0

        if person_filter not in contacts:
            contacts[person_filter] = 0
        if person_filter not in contacts_sent:
            contacts_sent[person_filter] = 0
        if person_filter not in contacts_recv:
            contacts_recv[person_filter] = 0

        if contacts[person_filter] != 0:
            filter_sent_percent = float(contacts_sent[person_filter]) / \
                    contacts[person_filter] * 100
            filter_recv_percent = float(contacts_recv[person_filter]) / \
                    contacts[person_filter] * 100

        print 'Total SMSs for %s:\t%5d\t100.00%%' % (person_filter,
                contacts[person_filter])
        print '\tSent:    \t\t%5d\t%6.2f%%' % (contacts_sent[person_filter], 
                filter_sent_percent) 
        print '\tReceived:\t\t%5d\t%6.2f%%' % (contacts_recv[person_filter], 
                filter_recv_percent)
        print

    if is_person_filter_on:
        print 'Monthly SMS activity for %s:' % (person_filter)
    else:
        print 'Monthly SMS activity:'
    for i in xrange(1, 13):
        print '\t%2s\t\t%5d\t' % (month_names[i], months[i]),
        for j in xrange(0, month_blocks[i]):
            sys.stdout.write('#')
        print
    sys.stdout.flush()
    print

    if is_person_filter_on:
        print 'Daily SMS activity for %s:' % (person_filter)
    else:
        print 'Daily SMS activity:'
    for i in xrange(0, 7):
        print '\t%2s\t\t%5d\t' % (day_names[i], days[i]),
        for j in xrange(0, day_blocks[i]):
            sys.stdout.write('#')
        print
    sys.stdout.flush()
    print

    if is_person_filter_on:
        print 'Hourly SMS activity for %s:' % (person_filter)
    else:
        print 'Hourly SMS activity:'
    for i in xrange(0, 24):
        print '\t%02d:     \t\t%5d\t' % (i, hours[i]),
        for j in xrange(0, hour_blocks[i]):
            sys.stdout.write('#')
        print
    sys.stdout.flush()
    print

if __name__ == "__main__": main()
