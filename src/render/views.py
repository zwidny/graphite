# -*- coding: utf-8 -*-
from __future__ import absolute_import
from time import time

from .utils.glyph import GraphTypes


def renderView(request):
    start = time()
    (graphOptions, requestOptions) = parseOptions(request)
    useCache = 'noCache' not in requestOptions
    cacheTimeout = requestOptions['cacheTimeout']
    requestContext = {
        'startTime': requestOptions['startTime'],
        'endTime': requestOptions['endTime'],
        'localOnly': requestOptions['localOnly'],
        'template': requestOptions['template'],
        'data': []
    }
    data = requestContext['data']

    # First we check the request cache
    if useCache:
        requestKey = hashRequest(request)
        cachedResponse = cache.get(requestKey)
        if cachedResponse:
            log.cache('Request-Cache hit [%s]' % requestKey)
            log.rendering('Returned cached response in %.6f' %
                          (time() - start))
            return cachedResponse
        else:
            log.cache('Request-Cache miss [%s]' % requestKey)

    # Now we prepare the requested data
    if requestOptions['graphType'] == 'pie':
        for target in requestOptions['targets']:
            if target.find(':') >= 0:
                try:
                    name, value = target.split(':', 1)
                    value = float(value)
                except:
                    raise ValueError("Invalid target '%s'" % target)
                data.append((name, value))
            else:
                seriesList = evaluateTarget(requestContext, target)

                for series in seriesList:
                    func = PieFunctions[requestOptions['pieMode']]
                    data.append(
                        (series.name, func(requestContext, series) or 0))

    elif requestOptions['graphType'] == 'line':
        # Let's see if at least our data is cached
        if useCache:
            targets = requestOptions['targets']
            startTime = requestOptions['startTime']
            endTime = requestOptions['endTime']
            dataKey = hashData(targets, startTime, endTime)
            cachedData = cache.get(dataKey)
            if cachedData:
                log.cache("Data-Cache hit [%s]" % dataKey)
            else:
                log.cache("Data-Cache miss [%s]" % dataKey)
        else:
            cachedData = None

        if cachedData is not None:
            requestContext['data'] = data = cachedData
        else:  # Have to actually retrieve the data now
            for target in requestOptions['targets']:
                if not target.strip():
                    continue
                t = time()
                seriesList = evaluateTarget(requestContext, target)
                log.rendering("Retrieval of %s took %.6f" %
                              (target, time() - t))
                data.extend(seriesList)

            if useCache:
                cache.add(dataKey, data, cacheTimeout)

        # If data is all we needed, we're done
        format = requestOptions.get('format')
        if format == 'csv':
            response = HttpResponse(content_type='text/csv')
            writer = csv.writer(response, dialect='excel')

            for series in data:
                for i, value in enumerate(series):
                    timestamp = datetime.fromtimestamp(
                        series.start + (i * series.step), requestOptions['tzinfo'])
                    writer.writerow(
                        (series.name, timestamp.strftime("%Y-%m-%d %H:%M:%S"), value))

            return response

        if format == 'json':
            series_data = []
            if 'maxDataPoints' in requestOptions and any(data):
                startTime = min([series.start for series in data])
                endTime = max([series.end for series in data])
                timeRange = endTime - startTime
                maxDataPoints = requestOptions['maxDataPoints']
                for series in data:
                    numberOfDataPoints = timeRange / series.step
                    if maxDataPoints < numberOfDataPoints:
                        valuesPerPoint = math.ceil(
                            float(numberOfDataPoints) / float(maxDataPoints))
                        secondsPerPoint = int(valuesPerPoint * series.step)
                        # Nudge start over a little bit so that the consolidation bands align with each call
                        # removing 'jitter' seen when refreshing.
                        nudge = secondsPerPoint + \
                            (series.start % series.step) - \
                            (series.start % secondsPerPoint)
                        series.start = series.start + nudge
                        valuesToLose = int(nudge / series.step)
                        for r in range(1, valuesToLose):
                            del series[0]
                        series.consolidate(valuesPerPoint)
                        timestamps = range(int(series.start), int(
                            series.end) + 1, int(secondsPerPoint))
                    else:
                        timestamps = range(int(series.start), int(
                            series.end) + 1, int(series.step))
                    datapoints = zip(series, timestamps)
                    series_data.append(
                        dict(target=series.name, datapoints=datapoints))
            else:
                for series in data:
                    timestamps = range(int(series.start), int(
                        series.end) + 1, int(series.step))
                    datapoints = zip(series, timestamps)
                    series_data.append(
                        dict(target=series.name, datapoints=datapoints))

            if 'jsonp' in requestOptions:
                response = HttpResponse(
                    content="%s(%s)" % (requestOptions[
                        'jsonp'], json.dumps(series_data)),
                    content_type='text/javascript')
            else:
                response = HttpResponse(content=json.dumps(series_data),
                                        content_type='application/json')

            if useCache:
                cache.add(requestKey, response, cacheTimeout)
                patch_response_headers(response, cache_timeout=cacheTimeout)
            else:
                add_never_cache_headers(response)
            return response

        if format == 'raw':
            response = HttpResponse(content_type='text/plain')
            for series in data:
                response.write("%s,%d,%d,%d|" % (
                    series.name, series.start, series.end, series.step))
                response.write(','.join(map(str, series)))
                response.write('\n')

            log.rendering('Total rawData rendering time %.6f' %
                          (time() - start))
            return response

        if format == 'svg':
            graphOptions['outputFormat'] = 'svg'

        if format == 'pickle':
            response = HttpResponse(content_type='application/pickle')
            seriesInfo = [series.getInfo() for series in data]
            pickle.dump(seriesInfo, response, protocol=-1)

            log.rendering('Total pickle rendering time %.6f' %
                          (time() - start))
            return response

    # We've got the data, now to render it
    graphOptions['data'] = data
    if settings.REMOTE_RENDERING:  # Rendering on other machines is faster in some situations
        image = delegateRendering(requestOptions['graphType'], graphOptions)
    else:
        image = doImageRender(requestOptions['graphClass'], graphOptions)

    useSVG = graphOptions.get('outputFormat') == 'svg'
    if useSVG and 'jsonp' in requestOptions:
        response = HttpResponse(
            content="%s(%s)" % (requestOptions['jsonp'], json.dumps(image)),
            content_type='text/javascript')
    else:
        response = buildResponse(
            image, 'image/svg+xml' if useSVG else 'image/png')

    if useCache:
        cache.add(requestKey, response, cacheTimeout)
        patch_response_headers(response, cache_timeout=cacheTimeout)
    else:
        add_never_cache_headers(response)

    log.rendering('Total rendering time %.6f seconds' % (time() - start))
    return response


def parseOptions(request):
    queryParams = request.REQUEST

    # Start with some defaults
    graphOptions = {'width': 330, 'height': 250}
    requestOptions = {}

    graphType = queryParams.get('graphType', 'line')
    assert graphType in GraphTypes, "Invalid graphType '%s', must be one of %s" % (
        graphType, GraphTypes.keys())
    graphClass = GraphTypes[graphType]

    # Fill in the requestOptions
    requestOptions['graphType'] = graphType
    requestOptions['graphClass'] = graphClass
    requestOptions['pieMode'] = queryParams.get('pieMode', 'average')
    requestOptions['cacheTimeout'] = int(queryParams.get(
        'cacheTimeout', settings.DEFAULT_CACHE_DURATION))
    requestOptions['targets'] = []

    # Extract the targets out of the queryParams
    mytargets = []
    # Normal format: ?target=path.1&target=path.2
    if len(queryParams.getlist('target')) > 0:
        mytargets = queryParams.getlist('target')

    # Rails/PHP/jQuery common practice format: ?target[]=path.1&target[]=path.2
    elif len(queryParams.getlist('target[]')) > 0:
        mytargets = queryParams.getlist('target[]')

    # Collect the targets
    for target in mytargets:
        requestOptions['targets'].append(target)

    template = dict()
    for key, val in queryParams.items():
        if key.startswith("template["):
            template[key[9:-1]] = val
    requestOptions['template'] = template

    if 'pickle' in queryParams:
        requestOptions['format'] = 'pickle'
    if 'rawData' in queryParams:
        requestOptions['format'] = 'raw'
    if 'format' in queryParams:
        requestOptions['format'] = queryParams['format']
        if 'jsonp' in queryParams:
            requestOptions['jsonp'] = queryParams['jsonp']
    if 'noCache' in queryParams:
        requestOptions['noCache'] = True
    if 'maxDataPoints' in queryParams and queryParams['maxDataPoints'].isdigit():
        requestOptions['maxDataPoints'] = int(queryParams['maxDataPoints'])

    requestOptions['localOnly'] = queryParams.get('local') == '1'

    # Fill in the graphOptions
    for opt in graphClass.customizable:
        if opt in queryParams:
            val = queryParams[opt]
            if (val.isdigit() or (val.startswith('-') and val[1:].isdigit())) and 'color' not in opt.lower():
                val = int(val)
            elif '.' in val and (val.replace('.', '', 1).isdigit() or (val.startswith('-') and val[1:].replace('.', '', 1).isdigit())):
                val = float(val)
            elif val.lower() in ('true', 'false'):
                val = val.lower() == 'true'
            elif val.lower() == 'default' or val == '':
                continue
            graphOptions[opt] = val

    tzinfo = pytz.timezone(settings.TIME_ZONE)
    if 'tz' in queryParams:
        try:
            tzinfo = pytz.timezone(queryParams['tz'])
        except pytz.UnknownTimeZoneError:
            pass
    requestOptions['tzinfo'] = tzinfo

    # Get the time interval for time-oriented graph types
    if graphType == 'line' or graphType == 'pie':
        if 'until' in queryParams:
            untilTime = parseATTime(queryParams['until'], tzinfo)
        else:
            untilTime = parseATTime('now', tzinfo)
        if 'from' in queryParams:
            fromTime = parseATTime(queryParams['from'], tzinfo)
        else:
            fromTime = parseATTime('-1d', tzinfo)

        startTime = min(fromTime, untilTime)
        endTime = max(fromTime, untilTime)
        assert startTime != endTime, "Invalid empty time range"

        requestOptions['startTime'] = startTime
        requestOptions['endTime'] = endTime
        timeRange = endTime - startTime
        # convert the time delta to seconds
        queryTime = timeRange.days * 86400 + timeRange.seconds
        if settings.DEFAULT_CACHE_POLICY and not queryParams.get('cacheTimeout'):
            requestOptions['cacheTimeout'] = max(
                timeout for period, timeout in settings.DEFAULT_CACHE_POLICY if period <= queryTime)

    return (graphOptions, requestOptions)
